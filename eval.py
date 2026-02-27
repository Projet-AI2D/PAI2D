import instance 
import matplotlib.pyplot as plt


red = [instance.majority_trois_quart, instance.condorcet_etendu]
res = [instance.resolution_dyn, instance.resolution_pl]
rec = [instance.reconstruction_classement_PDyn, instance.reconstruction_classement_PL]


def eval_temps(nomfich,fichDest="eval_temps.txt") : 
    
    f = open(fichDest,'a')
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich)+ ',')
    f.write(str(inst.nb_candidats))

    for rs in range(len(res)) : 
        for rd in red :
            f.write(',' + str(instance.resolution(inst, res[rs], rec[rs], rd)[0])) #avec une réduction
        f.write(',' + str(instance.resolution(inst, res[rs], rec[rs], red[0],red[1])[0]))#3/4 puis condorcet
        f.write(',' + str(instance.resolution(inst, res[rs], rec[rs],red[1],red[0])[0]))#condorcet puis 3/4  
        f.write(',' + str(instance.resolution(inst, res[rs],rec[rs])[0])) #sans reduction
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

eval_allFiles("00043 - cycling")

import pandas as pd

def courbe(fichSource='eval_reduction.csv',fichDest='courbe_reduction.png',reduction = True):
    df = pd.read_csv(fichSource)
    #print(df)
    if reduction :
        type_colonne = ['taille_max_3/4','Nb_candidats_fixes_3/4','taille_max_CCE','Nb_candidats_fixes_CCE']
    else : 
        type_colonne = ['3/4Maj+ProgDyn','CCE+ProgDyn','3/4Maj+CCE+ProgDyn','CCE+3/4Maj+ProgDyn','3/4Maj+PL','CCE+PL','3/4Maj+CCE+PL','CCE+3/4Maj+PL','PL']

    res = df.groupby(['Nb_candidats'])[type_colonne].mean()
    print(res)
    res.plot(y=type_colonne,marker='*') #Nb_candidats est déja l'index pour x
    plt.savefig(fichDest)

    plt.show()


courbe() #par défaut courbe de reduction
courbe(fichSource='eval_temps.csv',fichDest='courbe_reduction.png',reduction=False)#courbe du temps en fonction de la taille de l'instance