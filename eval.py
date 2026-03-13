import instance 
import matplotlib.pyplot as plt


red = [instance.majority_trois_quart, instance.condorcet_etendu]
res = [instance.resolution_dyn, instance.resolution_pl]
rec = [instance.reconstruction_classement_PDyn, instance.reconstruction_classement_PL]

import multiprocessing as mp

def run_with_timeout(func, args=(), timeout=600):
    pool = mp.Pool(processes=1)
    result = pool.apply_async(func, args=args)
    try:
        return result.get(timeout=timeout)
    except mp.TimeoutError:
        pool.terminate()
        pool.join()
        return "TIMEOUT"



def eval_temps(nomfich,fichDest="eval_temps.csv") : 
    
    f = open(fichDest,'a')
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich)+ ',')
    f.write(str(inst.nb_candidats))

    for rs in range(len(res)) : 
        for rd in red :
            #avec une reduction
            val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs], rd), timeout=2700)
            if val == "TIMEOUT":
                f.write(",TIMEOUT")
            else:
                f.write("," + str(val[0]))

        #3/4 puis condorcet
        val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs], red[0],red[1]), timeout=2700)
        if val == "TIMEOUT":
            f.write(",TIMEOUT")
        else:
            f.write("," + str(val[0]))
            
        #condorcet puis 3/4
        val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs],red[1],red[0]), timeout=2700)
        if val == "TIMEOUT":
            f.write(",TIMEOUT")
        else:
            f.write("," + str(val[0]))

        #sans reduction *
        if rs=='instance.resolution_dyn' and inst.nb_candidats > 150  :
            f.write(",TIMEOUT")
        else :
            val = run_with_timeout(instance.resolution,args=(inst, res[rs],rec[rs]), timeout=2700)
            if val == "TIMEOUT":
                f.write(",TIMEOUT")
            else:
                f.write("," + str(val[0]))

    f.write('\n')
    
    f.close()

#eval_temps("test.soc")

import csv 

def eval_reduction(nomfich,fichDest="eval_reduction.csv"): 
    f = open(fichDest,'a')
     
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich) + ',')
    f.write(str(inst.nb_candidats))

    for rd in red :
        nbmax = 0 
        nb_fixes =0
        classement = rd(inst)
        for i in classement : 
            if type(i) == instance.Instance:
                nbmax = max(nbmax,i.nb_candidats)
            else : 
                nb_fixes +=1
        f.write(',' + str(nbmax)+ ',' + str(nb_fixes))

    f.write('\n')
    
    f.close()



#eval_reduction("test.soc")

import os

def eval_allFiles(dataset="00004 - netflix"): 
    # f = open("eval_reduction.csv",'a')
    # writer = csv.writer(f)
    # writer.writerow(['nomFichier','Nb_candidats','taille_max_3/4','Nb_candidats_fixes_3/4','taille_max_CCE','Nb_candidats_fixes_CCE'])
    # f.close()

    # f = open("eval_temps.csv",'a')
    # writer = csv.writer(f)
    # writer.writerow(['nomFichier','Nb_candidats','3/4Maj+ProgDyn','CCE+ProgDyn','3/4Maj+CCE+ProgDyn','CCE+3/4Maj+ProgDyn','ProgDyn','3/4Maj+PL','CCE+PL','3/4Maj+CCE+PL','CCE+3/4Maj+PL','PL'])
    # f.close()

    # chemin du dossier
    dossier = os.path.join("./datasets", dataset)
    # parcourir tous les fichiers
    for fichier in os.listdir(dossier):
        chemin = os.path.join(dossier, fichier)
        if os.path.isfile(chemin):
            eval_temps(chemin)
            print("fin eval temps")
            eval_reduction(chemin)
            print("fin eval reduction")
            #47 et 49 et 52 pas fini
            #53
#on a pas lancé le 00015 et le 41 et 43 et 44 et 48 et 50 et 51 et 54 et 55 et 56 (45 et 46 et 49 à lancer demain
#enlever les fichiers dans spotifyday et relancer dessus
eval_allFiles("00053 - f1races")

# import pandas as pd

# def courbe(fichSource='eval_reduction.csv',fichDest='courbe_reduction.png',reduction = True):
#     df = pd.read_csv(fichSource)
#     #print(df)
#     if reduction :
#         type_colonne = ['taille_max_3/4','Nb_candidats_fixes_3/4','taille_max_CCE','Nb_candidats_fixes_CCE']
#     else : 
#         type_colonne = ['3/4Maj+ProgDyn','CCE+ProgDyn','3/4Maj+CCE+ProgDyn','CCE+3/4Maj+ProgDyn','3/4Maj+PL','CCE+PL','3/4Maj+CCE+PL','CCE+3/4Maj+PL','PL']

#     res = df.groupby(['Nb_candidats'])[type_colonne].mean()
#     print(res)
#     res.plot(y=type_colonne,marker='*') #Nb_candidats est déja l'index pour x
#     plt.savefig(fichDest)

#     plt.show()


# courbe() #par défaut courbe de reduction
# courbe(fichSource='eval_temps.csv',fichDest='courbe_reduction.png',reduction=False)#courbe du temps en fonction de la taille de l'instance