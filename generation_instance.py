# On ajoute le chemin du dossier 'top-k-mallows' au chemin de recherche de Python
import sys
sys.path.append("top-k-mallows")
import mallows_kendall as mk
import numpy as np
import instance 
import csv 
import pandas as pd
import matplotlib.pyplot as plt


ns = [50,100,500,994]     # Nombre de candidats (pr condorcet maximum recursion depth exceeded pour n>996 et pour 3/4 994)
m=1000 #nombre de votants
l_thetas = [0.00001, 0.0001,0.001,0.01,0.1,0.5,0.8,1, 2, 3] # aller jusqu'a 3 et faire plus de point entre 0 et 0.1 ; plus on avance plus on espace les evals
red = [instance.majority_trois_quart, instance.condorcet_etendu]

f = open("eval_generation_reduction.csv",'a')
writer = csv.writer(f)
writer.writerow(['N','theta','taille_max_3/4','taille_max_CCE'])
for n in ns : 
    s0 = np.arange(0,n) # Classement initial [0, 1, 2, ..., 9]
    for theta in l_thetas : # Paramètre de dispersion si theta proche de 0 => proba uniforme si theta proche de 1 => loi certaine de P

        for i in range(50) : #tester avec plusieurs profils differents
            # Générer un profil de préférence pour m votants et n candidats
            profil_preferences = mk.sample(m=m, n=n, theta=theta, s0=s0)

            inst = instance.Instance()
            inst.nb_candidats = n
            inst.nb_votants = m 

            inst.candidats = {}
            for j in range(n):
                inst.candidats[j+1] = str(j+1) 

            inst.matPref = np.zeros((n+1,n+1)) #matPref[k,j] = nb de votants qui preferent k à j, la premiere ligne et premiere colonnes sont vides pr avoir les bon indices
            # On boucle sur chaque vote du profil
            for pref in profil_preferences:
                # On parcourt toutes les paires de POSITIONS (k, j)
                for k in range(1,n+1): 
                    for j in range(k + 1, n+1): 
                        # Le candidat à la position k est préféré au candidat à la position j
                        inst.matPref[pref[k-1]+1, pref[j-1]+1] += 1
            inst.init = True

            f.write(str(theta))
            #taille max d'une sous instance
            for rd in red :
                print(theta, i ,' ', rd)
                classement = rd(inst)
                nbmax = 0 
                for i in classement : 
                    if type(i) == instance.Instance:
                        nbmax = max(nbmax,i.nb_candidats)
                f.write(',' + str(nbmax))
            f.write('\n')

f.close()
type_colonne = ['taille_max_3/4','taille_max_CCE']
df = pd.read_csv('eval_generation.csv')
res = df.groupby(['theta'])[type_colonne].mean()
#print(res)
res.plot(y=type_colonne,marker='*') #Nb_candidats est déja l'index pour x
plt.savefig('courbe_generation.png')
plt.show()

#print(instance.condorcet_etendu(inst))


#print(profil_preferences)
