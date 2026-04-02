import sys
sys.path.append("top-k-mallows") # ajout du chemin du dossier 'top-k-mallows' au chemin de recherche de Python

import mallows_kendall as mk
import numpy as np
import instance 
import csv 
import pandas as pd
import matplotlib.pyplot as plt

def generation_instance_mallows(n, m, theta):
    """Génère une instance à l'aide du profil de préférence créé avec le modèle de Mallows.  

    Paramètres
    ----------
    m: int
        Nombres de votants
    n: int
        Nombre de candidats
    theta: float
        Paramètre de dispersion
        
    Sortie
    -------
    Instance
        L'instance générée.

    Note:
    -----
    Le dossier top-k-mallows et plus précisément la fonction sample utilisée proviennent du dépôt GitHub de ekhiru.
    Dépôt : https://github.com/ekhiru/top-k-mallows.git

    """
   
    s0 = np.arange(m)# Classement initial [0, 1, 2, ..., 9] pour le modèle de Mallows 
    profil_preferences = mk.sample(m=n, n=m, theta=theta, s0=s0) #ndarray des preferences générées à l'aide du modèle de Mallows

    #creation de l'instance a partir du profil généré 
    inst = instance.Instance()
    inst.nb_candidats = m
    inst.nb_votants = n 
    inst.candidats = {j + 1: str(j + 1) for j in range(m)}
    
    #creation de la matrice de préférence
    matPref = np.zeros((m + 1, m + 1))
    for pref in profil_preferences: #on parcourt chaque préférences
        for k in range(1,m+1): 
            for j in range(k + 1, m+1): 
                # Le candidat à la position k est préféré au candidat à la position j car k < j
                matPref[pref[k-1]+1, pref[j-1]+1] += 1
            
    inst.matPref = matPref    
    inst.init = True
    return inst

def courbe_reduction(csv_path):
    """Gère la partie graphique de eval_generation_reduction."""

    type_colonne = ['taille_max_3/4','taille_max_CCE']
    df = pd.read_csv('eval_generation_reduction.csv')
    res = df.groupby(['theta'])[type_colonne].mean()
    res.plot(y=type_colonne,marker='*') #Nb_candidats est déja l'index pour x
    plt.savefig('courbe_generation_reduction_theta.png')
    plt.show()



def eval_generation_reduction(): 
    """ Évalue la règle des 3/4 et le critère de Condorcet étendu sur des instances synthétiques.
    Génère des instances en faisant varier indépendamment le paramètre theta (dispersion) et le nombre de candidats.  
    Pour chaque instance, applique les deux méthodes de décomposition et calcule la taille de la plus grande sous-instance obtenue pour chaque méthodes. 
    Les résultats sont reportés dans le fichier 'eval_generation_reduction.csv'.

    Paramètres
    ----------
    Aucun.

    Sortie
    -------
    Aucune.

    Effets de bord
    ----------------------------
    Écrit ou écrase le fichier 'eval_generation_reduction.csv' dans le répertoire courant.

    """

    l_m = [50,100,500,994] #liste des valeurs testées pour m (maximum recursion depth exceeded pour n>994 pour la règle des 3/4 )
    n=1000 #nombre de votants
    l_thetas = [0.00001, 0.0001,0.001,0.01,0.1,0.5,0.8,1, 2, 3] # liste des valeurs testées pour theta
    red = [instance.majority_trois_quart, instance.condorcet_etendu] #liste des méthodes de reduction

    f = open("eval_generation_reduction.csv",'a')
    writer = csv.writer(f)
    writer.writerow(['m','theta','taille_max_3/4','taille_max_CCE'])
    
    for m in l_m : 
        for theta in l_thetas : # Paramètre de dispersion si theta proche de 0 => proba uniforme si theta proche de 1 => loi certaine de P
            for i in range(50) : #tester plusieurs profils differents
        
                inst= generation_instance_mallows(n,m,theta) #Générer un profil de préférence pour n votants et m candidats
                f.write(str(m) + ',' +str(theta))

                for rd in red :
                    print(theta, i ,' ', rd)
                    classement = rd(inst) #réduction de l'instance

                    #calcul de la taille max d'une sous instance
                    nbmax = 0 
                    for i in classement : 
                        if type(i) == instance.Instance: #si le type n'est pas une instance, c'est un candidat qu'on sait déja positionner dans le classement
                            nbmax = max(nbmax,i.nb_candidats)
                    f.write(',' + str(nbmax))
                f.write('\n')

    f.close()

def eval_generation_PL_CCE():
    """ Évalue l'impact du critère de Condorcet étendu sur le temps d'exécution de la programmation linéaire.

    Génère des instances en faisant varier indépendamment le nombre de candidats (n) et 
    le paramètre theta. Pour chaque instance, compare deux approches :
    1. Résolution par programmation linéaire (PL) directe sur l'instance complète.
    2. Réduction préalable via le critère de Condorcet étendu, puis résolution par PL 
    des sous-instances obtenues.

    Les temps d'exécution respectifs sont enregistrés dans 'eval_generation_PL.csv' 
    pour mesurer le gain d'efficacité apporté par la réduction.

    Paramètres
    ----------
    Aucun.

    Effets de bord
    --------------
    Écrit ou écrase le fichier 'eval_generation_PL.csv' dans le répertoire courant.
    """

    n=1000 #nombre de votants    
    l_thetas = [0.00001, 0.0001,0.001,0.01,0.1] #condorcet réduit suffisamment avec theta = 0.1
    l_m = [50,100,500,994] #liste des valeurs testées pour m (maximum recursion depth exceeded pour n>994 pour la règle des 3/4 )
 
    f = open("eval_generation_PL.csv",'a')

    writer = csv.writer(f)
    writer.writerow(['m','theta','temps_PL_sans_CCE','temps_PL_avec_CCE'])


    #on fait varier theta et m indépendamment 
    for m in l_m : 
        for theta in l_thetas : 
            for i in range(50) : #tester avec plusieurs profils differents

                inst = generation_instance_mallows(n,m,theta) #generation d'une instance 

                f.write(str(m) + ',' +str(theta))

                print(m, i,'sans CCE')
                temps, _ = instance.resolution(inst, instance.resolution_pl, instance.reconstruction_classement_PL) #résolution avec PL sans CCE 
                f.write(',' + str(temps))

                print(m, i,'avec CCE')
                temps, _ = instance.resolution(inst, instance.resolution_pl, instance.reconstruction_classement_PL,reduction1=instance.condorcet_etendu) #resolution avec CCE puis PL
                f.write(',' + str(temps))
                
                f.write('\n')
    f.close()

if __name__ == "__main__":
    eval_generation_reduction()
    eval_generation_PL_CCE()
    courbe_reduction()