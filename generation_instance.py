import sys
sys.path.append("top-k-mallows") # ajout du chemin du dossier 'top-k-mallows' au chemin de recherche de Python

import mallows_kendall as mk
import numpy as np
import instance 
import csv 
import pandas as pd
import matplotlib.pyplot as plt
import eval 

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
    l_thetas = [0.00001,0.00002,0.00003,0.00004,0.00005,0.00006,0.00007,0.00008,0.00009, 0.0001,0.001,0.005,0.01,0.02 ,0.05,0.1,0.5,0.8,1, 2, 3] # liste des valeurs testées pour theta
    red = [instance.majorite_trois_quart, instance.condorcet_etendu] #liste des méthodes de reduction

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

    Sortie
    --------------
    Écrit ou écrase le fichier 'eval_generation_PL.csv' dans le répertoire courant.
    """

    n=1000 #nombre de votants    
    l_thetas = [0.00001, 0.0001,0.001,0.01,0.1] #condorcet réduit suffisamment avec theta = 0.1
    l_m = [50,100,200,300,400,500] #liste des valeurs testées pour m (maximum recursion depth exceeded pour n>994 pour la règle des 3/4 )
    
    f = open("eval_generation_PL.csv",'a')

    writer = csv.writer(f)
    writer.writerow(['m','theta','temps_PL_sans_CCE','temps_PL_avec_CCE'])

    f.close()

    #on fait varier theta et m indépendamment 
    for m in l_m : 
        for theta in l_thetas : 
            for i in range(10) : #tester avec plusieurs profils differents
                f = open("eval_generation_PL.csv",'a')

                inst = generation_instance_mallows(n,m,theta) #generation d'une instance 

                f.write(str(m) + ',' +str(theta))

                print(m, i,'sans CCE')
                val = eval.run_with_timeout(instance.resolution,args=(inst, instance.resolution_pl, instance.reconstruction_classement_PL), timeout=2700)
                # val est un couple (temps,classement)
                if val == "TIMEOUT":
                    f.write(",2700")
                else:
                    f.write("," + str(val[0])) 


                print(m, i,'avec CCE')
                val = eval.run_with_timeout(instance.resolution,args=(inst, instance.resolution_pl, instance.reconstruction_classement_PL,instance.condorcet_etendu), timeout=2700)
                if val == "TIMEOUT":
                    f.write(",2700")
                else:
                    f.write("," + str(val[0]))

                
                f.write('\n')

                f.close()



def courbe_PL(chemin_csv="eval_generation_PL.csv", fichDest="courbe_PL_CCE.png"):
    """Génère et sauvegarde des graphiques comparant les temps de résolution des 
    Programmes Linéaires (PL) avec et sans l'optimisation CCE.

    Paramètres
    ----------
    chemin_csv : str
        Chemin d'accès vers le fichier CSV contenant les données d'évaluation.
    fichDest : str
        fichier image de sortie pour sauvegarder les courbes

    Sortie 
    ----------
    Sauvegarde les courbes dans le fichier fichDest.

    """

    df = pd.read_csv(chemin_csv)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Figure 1 : Impact de m (à theta = 0.1) 
    df_m = df[df['theta'] == 0.01]
    # Groupement par m et calcul de la médiane
    res_m = df_m.groupby('m')[['temps_PL_sans_CCE', 'temps_PL_avec_CCE']].median()

    ax1.plot(res_m.index, res_m['temps_PL_sans_CCE'], label='PL sans CCE')
    ax1.plot(res_m.index, res_m['temps_PL_avec_CCE'],label='PL + CCE')

    ax1.set_title("Influence du nombre de candidats (m)\n(pour θ = 0.1)")
    ax1.set_xlabel("Nombre de candidats (m)")
    ax1.set_ylabel("Temps médian (s)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Figure 2 : Impact de theta (à m = 500)
    df_theta = df[df['m'] == 400]
    # Groupement par theta et calcul de la médiane
    res_theta = df_theta.groupby('theta')[['temps_PL_sans_CCE', 'temps_PL_avec_CCE']].median()

    ax2.plot(res_theta.index, res_theta['temps_PL_sans_CCE'], label='PL sans CCE')
    ax2.plot(res_theta.index, res_theta['temps_PL_avec_CCE'], label='PL avec CCE')

    ax2.set_title("Influence de la cohérence des votes (θ)\n(pour m = 400)")
    ax2.set_xlabel("theta (θ)")
    ax2.set_ylabel("Temps médian (s)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.suptitle("Comparaison des temps de résolution : PL avec et sans CCE", fontsize=14)
    plt.tight_layout()
    plt.savefig(fichDest)
    plt.show()


def courbes_reduction_theta(chemin_csv="eval_generation_reduction.csv", m=500, fichDest="courbes_generation_reduction_theta.png"):
    """Génère et sauvegarde des graphiques comparant la taille maximale moyenne des sous instance en fonction de theta.

    Paramètres
    ----------
    chemin_csv : str
        Chemin d'accès vers le fichier CSV contenant les données d'évaluation.
    fichDest : str
        fichier image de sortie pour sauvegarder les courbes

    Sortie 
    ----------
    Sauvegarde les courbes dans le fichier fichDest.
    
    """
    
    df = pd.read_csv(chemin_csv)

    # Filtre sur m et agrégation par theta
    df_m = df[df["m"] == m]
    df_grouped = df_m.groupby("theta")[["taille_max_3/4", "taille_max_CCE"]].mean().reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, (xlim, title) in zip(axes, [
        (None,       f"Efficacité de la réduction selon theta (m = {m})"),
        ((0, 0.1),   "Zoom theta (0 - 0.1)"),
    ]):
        ax.plot(df_grouped["theta"], df_grouped["taille_max_3/4"],
                label="3/4 majorité")
        ax.plot(df_grouped["theta"], df_grouped["taille_max_CCE"],
                label="Condorcet étendu")
        ax.set_title(title)
        ax.set_xlabel("Theta", fontsize=11)
        ax.set_ylabel("Taille max moyenne", fontsize=11)
        ax.legend(title="Algorithmes", fontsize=9)
        if xlim:
            ax.set_xlim(xlim)

    plt.tight_layout()
    plt.savefig(fichDest)
    plt.show()


def courbe_reduction_m(chemin_csv='eval_generation_reduction.csv',fichDest='courbes_generation_reduction_m.png'):
    """Génère et sauvegarde des courbes comparant l'impact du nombre de candidats (m) sur l'efficacité des algorithmes de réduction (Majorité 3/4 et Condorcet étendu).

    Chaque graphique affiche trois courbes correspondant à différentes valeurs de theta (0.01, 1 et 3) pour observer comment la cohérence des votes interagit avec la taille de l'instance.

    Paramètres
    ----------
    chemin_csv : str
        Chemin d'accès vers le fichier CSV contenant les données d'évaluation.
    fichDest : str
        fichier image de sortie pour sauvegarder les courbes

    Sortie 
    ----------
    Sauvegarde les courbes dans le fichier fichDest.
    

    """
    df = pd.read_csv(chemin_csv)
    thetas = [0.01, 1, 3]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    for idx, t in enumerate(thetas):
        mask = np.isclose(df['theta'], t, atol=1e-8)
        data = df[mask]
    
        # Courbe pour 3/4 Majorité 
        res_34 = data.groupby('m')['taille_max_3/4'].mean().sort_index()
        ax1.plot(res_34.index, res_34.values, label=f"θ={t}")
        
        # Courbe pour CCE 
        res_cce = data.groupby('m')['taille_max_CCE'].mean().sort_index()
        ax2.plot(res_cce.index, res_cce.values, label=f"θ={t}")

    ax1.set_title("3/4-Majorité ")
    ax1.set_ylabel("Taille max")
    ax1.set_xlabel("Nombre de candidats")
    ax1.grid(True,which="both", alpha=0.3)
    ax1.legend()

    ax2.set_title("Critère de condorcet étendu")
    ax2.set_ylabel("Taille max")
    ax2.set_xlabel("Nombre de candidats")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.suptitle("Efficacité des réductions selon le nombre de candidats et θ")

    plt.tight_layout()
    plt.savefig(fichDest, bbox_inches='tight') # bbox_inches évite que le titre soit coupé
    plt.show()



if __name__ == "__main__":
    #courbe_PL()
    courbe_reduction_m()
    #courbes_reduction_theta()
    

