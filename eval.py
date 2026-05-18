import instance 
import matplotlib.pyplot as plt
import os
import multiprocessing as mp
import csv
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm


red = [instance.majorite_trois_quart, instance.condorcet_etendu]
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
            si la fonction est exécutée dans le temps imparti la sortie est identique à celle de la fonction executée
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


def eval_temps(nomfich,fichDest="eval_temps.csv") : 
    """ Cette fonction permet de conserver les temps d'execution (avec une limite de temps : 45 min) dans un fichier.
        Elle commence par lire l'instance  puis appelle toutes les combinaisons de méthodes de décompostions et de résolutions
    
        Paramètres
        ----------
        nonfich: str
            nom du fichier qui contient l'instance à lire
        fichDest: str 
            nom du fichier dans lequel on stocke les resultats 
            
        Sortie
        -------
        Sauvegarde les résultats dans le fichier fichDest
    """
    
    f = open(fichDest,'a')
    inst = instance.Instance()
    temps_matpref = inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich)+ ',') #ne garder que le nom du fichier et non tout le chemin
    f.write(str(inst.nb_candidats))

    for rs in range(len(res)) : 
        for rd in red :
            #avec une reduction
            if res[rs]==instance.resolution_dyn and inst.nb_candidats > 200  :  
                f.write(",2700")
            else : 
                val = run_with_timeout(instance.resolution,args=(inst, res[rs], rec[rs], rd), timeout=2700) #renvoie le couple (temps,classement)
                if val == "TIMEOUT":
                    f.write(",2700")
                else:
                    f.write("," + str(temps_matpref+val[0])) #temps d'execution et de construction de la matrice

        #sans reduction 
        if res[rs]==instance.resolution_dyn and inst.nb_candidats > 100  : #pour plus de 100 candidats la PDyn est inefficace
            f.write(",2700")
        else :
            val = run_with_timeout(instance.resolution,args=(inst, res[rs],rec[rs]), timeout=2700)
            if val == "TIMEOUT":
                f.write(",2700")
            else:
                f.write("," + str(temps_matpref+val[0]))

    f.write('\n')
    
    f.close()


def eval_reduction(nomfich,fichDest): 
    """ Cette fonction permet de conserver les performances (la taille de la plus grande sous-instance et le nombre de candidat dont la position est connue après décomposition) dans un fichier.
        Elle commence par lire l'instance  puis appelle les méthodes de décompostions
    
        Paramètres
        ----------
        nonfich: str
            nom du fichier qui contient l'instance à lire
        fichDest: str
            nom du fichier dans lequel on stocke les performances 
            
        Sortie
        -------
        Sauvegarde les résultats dans le fichier fichDest
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


def reduction_allFiles(fichDest="eval_reduction.csv"):
    """ Cette fonction permet d'appeler eval_reduction sur tous les fichiers du dataset.
        
        Paramètres
            ----------
            fichDest: str
                nom du fichier dans lequel on stocke les performances 
        
        Sortie
        -------
        Sauvegarde les résultats dans le fichier fichDest
        
    """

    f = open(fichDest,'a')
    writer = csv.writer(f)
    writer.writerow(['nomFichier','Nb_candidats','taille_max_3/4','Nb_candidats_fixes_3/4','taille_max_CCE','Nb_candidats_fixes_CCE'])
    f.close()

    root_dir = './datasets'

    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            # Créer le chemin complet
            filepath = os.path.join(root, filename)
            
            # Lancer la fonction de réduction
            print(f"Réduction de {filepath}")
            eval_reduction(filepath,fichDest)


def temps_allFiles(dataset="00004 - netflix",fichDest='eval_temps.csv'): 
    """ Cette fonction permet d'appliquer eval_temps sur tous les fichiers d'un dossier du dataset.

        Paramètres
        ----------
        dataset: str
            nom du dossier qui contient plusieurs instances à évaluer
            
        Sortie
        -------
        Sauvegarde les résultats dans le fichier fichDest
    """
   
    f = open(fichDest,'a')
    writer = csv.writer(f)
    writer.writerow(['nomFichier','Nb_candidats','3/4Maj+ProgDyn','CCE+ProgDyn','3/4Maj+CCE+ProgDyn','CCE+3/4Maj+ProgDyn','ProgDyn','3/4Maj+PL','CCE+PL','3/4Maj+CCE+PL','CCE+3/4Maj+PL','PL'])
    f.close()

    # chemin du dossier
    dossier = os.path.join("./datasets", dataset)
    # parcourir tous les fichiers
    for fichier in os.listdir(dossier):
        chemin = os.path.join(dossier, fichier)  # chemin du fichier
        if os.path.isfile(chemin):
            eval_temps(chemin)
            

def tracer_courbes_reduction(chemin_csv="eval_reduction.csv", fichDest="courbes_reduction_PrefLib.png"):
    """Génère et sauvegarde les graphiques d'efficacité des règles de réduction.

    Cette fonction agrège les données par la moyenne selon le nombre de
    candidats initiaux, puis trace deux graphiques : la taille moyenne restante
    de la plus grande sous-instance et le nombre moyen de candidats fixés.

    Paramètres
    ----------
    chemin_csv : str
        Chemin vers le fichier CSV contenant les résultats de l'évaluation.
    fichDest : str
        fichier image de sortie à sauvegarder.

    Sortie
    ------
    Sauvegarde le graphique dans le fichier fichDest.
    """
        
    df = pd.read_csv(chemin_csv)

    # Agrégation par moyenne pour les deux graphiques
    df_grouped = df.groupby("Nb_candidats")[
        ["taille_max_3/4", "taille_max_CCE", "Nb_candidats_fixes_3/4", "Nb_candidats_fixes_CCE"]
    ].mean().reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Graphique 1 : candidats fixés 
    ax1 = axes[0]
    ax1.scatter(df_grouped["Nb_candidats"], df_grouped["Nb_candidats_fixes_3/4"],
                s=12, alpha=0.7, label="3/4 majorité")
    ax1.scatter(df_grouped["Nb_candidats"], df_grouped["Nb_candidats_fixes_CCE"],
                s=12, alpha=0.7, label="Condorcet étendu")
    ax1.set_title("Efficacité de la réduction :\ncandidats fixés")
    ax1.set_xlabel("Nombre de candidats", fontsize=11)
    ax1.set_ylabel("Nombre de candidats déjà fixés par la réduction", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(title="Algorithmes")

    # Graphique 2 : taille moyenne 
    ax2 = axes[1]
    ax2.scatter(df_grouped["Nb_candidats"], df_grouped["taille_max_3/4"],
                s=12, alpha=0.7, label="3/4 majorité")
    ax2.scatter(df_grouped["Nb_candidats"], df_grouped["taille_max_CCE"],
                s=12, alpha=0.7, label="Condorcet étendu")
    ax2.set_title("Efficacité de la réduction :\ntaille moyenne de la plus grande sous instance")
    ax2.set_xlabel("Nombre de candidats")
    ax2.set_ylabel("Taille moyenne")
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.legend(title="Algorithmes")

    plt.tight_layout()
    plt.savefig(fichDest)
    plt.show()
    

def heatmapTemps(chemin_csv='eval_temps.csv'):
    """Génère une heatmap des temps de résolution.

        Cette fonction charge les données d'évaluation temporelle, regroupe le nombre
        de candidats par tranches de tailles prédéfinies, calcule le temps médian
        de calcul pour chaque algorithme, puis représente graphiquement ces performances
        sur une échelle logarithmique.

        Paramètres
        ----------
        chemin_csv : str
            Chemin vers le fichier CSV contenant les résultats de l'évaluation.

        Sortie
        ------
        Sauvegarde le graphique dans le fichier fichDest.
        """

    df = pd.read_csv(chemin_csv)

    # Identification des colonnes
    algos_bruts = [col for col in df.columns[2:] if not ("3/4" in col and "CCE" in col)]

    # Dictionnaire pour renommer formellement
    traduction = {
        'ProgDyn': 'Prog. Dynamique seule',
        '3/4Maj+ProgDyn': r'$\frac{3}{4}$-Majorité + Prog. Dyn.',
        'CCE+ProgDyn': 'Condorcet étendu + Prog. Dyn.',
        'PL': 'Prog. Linéaire seule',
        '3/4Maj+PL': r'$\frac{3}{4}$-Majorité + Prog. Linéaire',
        'CCE+PL': 'Condorcet étendu + Prog. Linéaire'
    }


    # Tranches
    bins = [0, 9, 19, 29, 39, 49, 65, 75, 90, 100, 200, 300, 400]
    labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-65', '66-75', '76-90', '91-100', '101-200', '201-300', '301-400']
    df['Tranche'] = pd.cut(df['Nb_candidats'], bins=bins, labels=labels)
 
    # Médiane des temps, comptage et renommage
    heatmap_data = df.groupby('Tranche', observed=False)[algos_bruts].median().T
    counts = df['Tranche'].value_counts().reindex(labels).fillna(0).astype(int)
    
    # Format horizontal
    heatmap_data.columns = [f"{lab} ({counts[lab]} inst.)" for lab in labels]
    heatmap_data.index = [traduction.get(x, x) for x in heatmap_data.index]

    # Dessin
    plt.figure(figsize=(15, 8)) 
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="RdYlGn_r", 
                norm=LogNorm(vmin=0.001, vmax=2700))
    plt.xticks(rotation=30, ha='right') # Rotation pour la lisibilité


    plt.title("Analyse des performances : Temps médian de résolution (s)", fontsize=18)
    plt.xlabel("Nombre de candidats ($n$)", fontsize=12)
    plt.ylabel("Méthodes de résolution", fontsize=12)

    plt.tight_layout()
    plt.savefig('eval_temps.png')
    plt.show()


if __name__ == "__main__":
    #tracer_courbes_reduction()
    heatmapTemps()