import instance 
import matplotlib.pyplot as plt
import os
import multiprocessing as mp
import csv


red = [instance.majority_trois_quart, instance.condorcet_etendu]
res = [instance.resolution_dyn,instance.resolution_pl]
rec = [instance.reconstruction_classement_PDyn,instance.reconstruction_classement_PL]

def run_with_timeout(func, args=(), timeout=600):
    """ Cette fonction permet d'executer une fonction dans un temps limite timeout
    
        Paramètres
        ----------
        func: nom de la fonction à executer
        args: arguments de la fonction à executer 
            la fonction appelée prend en argument l'instance, la méthode de résolution,
            la fonction de reconstruction du classement, et la ou les méthodes de décomposition
            
        Sortie
        -------
        sortie de la fonction ou "TIMEOUT"
            si la fonction est exécutée dans le temps impartie la sortie est identique à celle de la fonction executée
            sinon la sortie est "TIMEOUT"
    """
    pool = mp.Pool(processes=1) #creer un pool processus pour executer la fonction dans un processus séparé
    result = pool.apply_async(func, args=args) #lance la fonction de facon asynchrone
    try:
        return result.get(timeout=timeout) #attend le resultat dans la limite de temps timeout
    except mp.TimeoutError:
        pool.terminate() #tuer le processus
        pool.join() #attend que tout soit bien nettoyé
        return "TIMEOUT"


#fichier = "./datasets/00045 - tennis/00045-00000027.soc"

def eval_temps(nomfich,fichDest="eval_temps.csv") : 
    """ Cette fonction permet de conserver les temps d'execution (avec une limite de temps : 45 min) dans un fichier.
        Elle commence par lire l'instance  puis appelle toutes les combinaisons de méthodes de décompostions et de résolutions
    
        Paramètres
        ----------
        nonfich: nom du fichier qui contient l'instance à lire
        fichDest: nom du fichier dans lequel on stocke les resultats 
            
        Sortie
        -------
        aucune sortie
    """
    
    f = open(fichDest,'a')
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich)+ ',') #ne garder que le nom du fichier et non tout le chemin
    f.write(str(inst.nb_candidats))

    for rs in range(len(res)) : 
        for rd in red :
            #avec une reduction
            if res[rs]==instance.resolution_dyn and inst.nb_candidats > 100  : 
                f.write(",TIMEOUT")
            else : 
                val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs], rd), timeout=2700)
                if val == "TIMEOUT":
                    f.write(",TIMEOUT")
                else:
                    f.write("," + str(val[0])) #notre fonction renvoie le couple (temps,classement)

        #3/4 puis condorcet
        if res[rs]==instance.resolution_dyn and inst.nb_candidats > 100  :
            f.write(",TIMEOUT")
        else :
            val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs], red[0],red[1]), timeout=2700)
            if val == "TIMEOUT":
                f.write(",TIMEOUT")
            else:
                f.write("," + str(val[0]))
            
        #condorcet puis 3/4
        if res[rs]==instance.resolution_dyn and inst.nb_candidats > 100  :
            f.write(",TIMEOUT")
        
        else : 
            val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs],red[1],red[0]), timeout=2700)
            if val == "TIMEOUT":
                f.write(",TIMEOUT")
            else:
                f.write("," + str(val[0]))

        #sans reduction 
        if res[rs]==instance.resolution_dyn and inst.nb_candidats > 100  :
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
# eval_temps(fichier)

def eval_reduction(nomfich,fichDest="eval_reduction.csv"): 
    """ Cette fonction permet de conserver les performances (la taille de la plus grande sous-instance et le nombre de candidat dont la position est connue après décomposition) dans un fichier.
        Elle commence par lire l'instance  puis appelle les méthodes de décompostions
    
        Paramètres
        ----------
        nonfich: nom du fichier qui contient l'instance à lire
        fichDest: nom du fichier dans lequel on stocke les performances 
            
        Sortie
        -------
        aucune sortie
    """
    f = open(fichDest,'a')
     
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich) + ',') #ne garder que le nom du fichier et non tout le chemin
    f.write(str(inst.nb_candidats))

    for rd in red :
        nbmax = 0 
        nb_fixes =0
        #une liste avec les candidats lorsque qu'ils sont fixés et un object Instance (sous-instance)
        classement = rd(inst)
        for i in classement : 
            if type(i) == instance.Instance:
                nbmax = max(nbmax,i.nb_candidats)
            else : 
                nb_fixes +=1
        f.write(',' + str(nbmax)+ ',' + str(nb_fixes))

    f.write('\n')
    
    f.close()



#eval_reduction(fichier)
# os.remove(fichier)


def eval_allFiles(dataset="00004 - netflix"): 
    """ Cette fonction permet d'appliquer les deux fonctions d'évaluation sur un dossier dataset (dossier avec plusieurs instances)
    
        Paramètres
        ----------
        dataset: nom du dossier qui contient plusieurs instances (à évaluer)
            
        Sortie
        -------
        aucune sortie
    """
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
        chemin = os.path.join(dossier, fichier)  # chemin du fichier
        if os.path.isfile(chemin):
            eval_temps(chemin)
            print("fin eval temps")
            #eval_reduction(chemin)
            print("fin eval reduction")
            os.rename(chemin,os.path.join("./datasets", fichier))
            #47 et 49 et 52 pas fini

#on a pas lancé le 00015 et le 41 et 43 et 44 et 48 et 50 et 51 et 54 et 55 et 56 (45 et 46 et 49 à lancer demain
#enlever les fichiers dans spotifyday et relancer dessus
eval_allFiles("00045 - tennis")


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
