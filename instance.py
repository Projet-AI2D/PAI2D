import numpy as np
import copy
from gurobipy import *

import sys
import os
preflib_path = "/users/Etu8/21233538/.local/lib/python3.11/site-packages"
if os.path.exists(preflib_path) and preflib_path not in sys.path:
    sys.path.insert(0, preflib_path)
    print(f"Chemin ajouté: {preflib_path}")

from preflibtools.instances import OrdinalInstance

import matplotlib.pyplot as plt
import networkx

class Instance :
    def __init__ (self) :
        self.init = False 
    
    def lecture_fichier(self,nomfich):
        inst = OrdinalInstance() 
        inst.parse_file(nomfich) #lecture de l'instance dans le fichier

        self.nb_votants = inst.num_voters # nombre de votants
        self.nb_candidats = inst.num_alternatives    # nombre d'alternatives
        self.candidats =  inst.alternatives_name   # dictionnaire cle=indice , valeur = nom alternative
        
        profil_preferences = {tuple(x[0] for x in k): v for k, v in inst.multiplicity.items()} #dictionnaire cle = classements et valeur = nombre d'apparition
        self.init = True
        self.comptage(profil_preferences)

    #a changer
    def comptage(self, profil) : 
        #si on garde pas le profil de preference on doit refaire ca ici : profil = {tuple(x[0] for x in k): v for k, v in inst.multiplicity.items()} 
        
        self.matPref = np.zeros((self.nb_candidats+1,self.nb_candidats+1)) #matPref[i,j] = nb de votants qui preferent i à j, la premiere ligne et premiere colonnes sont vides pr avoir les bon indices
        for pref, nbpref in profil.items() :
            for i in range(1,self.nb_candidats+1) : 
                for j in range(i+1, self.nb_candidats+1) : 
                    if pref.index(i) < pref.index(j):
                        self.matPref[i,j] += nbpref
                    else : 
                        self.matPref[j,i] += nbpref        


    #somme des dist de Kendall Tau
    def score_Kemeny(self, classement) : 
        if not self.init :
            print("Initialisez l'instance avec lecture_fichier")
            return -1
        score=0
        # for pref, nbpref in self.profil_preferences.items() :
        #     score +=  Kendall_Tau(pref, classement) * nbpref
        for i in classement :
            for j in classement[classement.index(i)+1:] :
                score += self.matPref[j,i]
        return score

    # def est_propre(self,cand,l_propres,l_sales) : 
    #     for i in self.candidats.keys() : 
    #         if i != cand and self.matPref[i,cand] < (3/4)*self.nb_votants and self.matPref[cand,i] < (3/4)*self.nb_votants :
    #             l_sales.append(cand)
    #             return False
    #     l_propres.append(cand)
    #     return True

    def est_propre(self,cand,candidats) : 
        l_avant = []
        l_apres = []
        propre = True
        for i in candidats : 
            if i == cand :
                continue 
            elif self.matPref[i,cand] >= (3/4)*self.nb_votants:
                l_avant.append(i) 
            elif self.matPref[cand,i] >= (3/4)*self.nb_votants :
                l_apres.append(i) 
            else :
                propre = False 
        if not propre :
            return l_avant, l_apres, False
        return l_avant, l_apres, True

    class Graphe :

        def __init__(self):
            self.noeuds = []
            self.voisins = dict()
        
        def __str__(self):
            s = "Noeuds :\n"
            for n in self.noeuds:
                s += f"  {n}\n"

            s += "Voisins :\n"
            for key, vals in self.voisins.items():
                s += f"  {key} -> {vals}\n"
            return s

        def getNoeuds(self):
            return self.noeuds 

        def addNoeud(self,cand):
            if cand not in self.noeuds:
                self.noeuds.append(cand)
                self.voisins[cand]=[]

        def addVoisins(self,cand1,cand2):
            # S'assurer que les noeuds existent
            self.addNoeud(cand1)
            self.addNoeud(cand2)
            
            if cand2 not in self.voisins[cand1]:
                self.voisins[cand1].append(cand2)

            #ajouter la marge sur les arcs?

        def getVoisins(self,cand):#recuperer les voisins    
            return self.voisins.get(cand,[]) #[] valeur par defaut
            
        

        #algorithme de tarjan 
        def get_CFC(self) : 
            num = 0
            pile = []
            partition = []

            numAccessible = {}
            numero = {}

            def DFS_recursif(sommetInit):
                nonlocal num, pile, partition,numAccessible,numero  # Déclare que num vient de la fonction parente
                pile.append(sommetInit) #noeud + lowlink
                numAccessible[sommetInit] = num
                numero[sommetInit] = num
                num += 1 

                for voisin in self.getVoisins(sommetInit) : 
                    print("v : ",voisin, " de : ", sommetInit)
                    if voisin not in numero:
                        DFS_recursif(voisin)
                        numAccessible[sommetInit] = min(numAccessible[sommetInit],numAccessible[voisin])
                        
                    elif voisin in pile:
                        #print("if")
                        numAccessible[sommetInit] = min(numAccessible[sommetInit],numero[voisin])
                        
                # print(pile)
                #print(lowlink)
                if numAccessible[sommetInit] == numero[sommetInit] : 
                    cfc = set()
                    w = pile.pop()
                    while w != sommetInit :
                        print(w)
                        cfc.add(w)
                        w = pile.pop()
                    cfc.add(w)
                    partition.append(cfc)
           

            for n in self.noeuds : 
                if n not in numAccessible.keys(): #si le noeud n'est dans aucune cfc (noeud isolé par exemple)
                    DFS_recursif(n)

            return partition
                
        #a modif
        def afficher_graphe(self):
            fig, ax = plt.subplots(figsize=(10, 8)) #fenetre d'affichage

            # 1. Positionner les noeuds sur un cercle 
            n = len(self.noeuds)
            positions = {}
            for i, noeud in enumerate(self.noeuds):
                angle = 2 * np.pi * i / n
                positions[noeud] = (np.cos(angle), np.sin(angle))

            # 2. Dessiner les NOEUDS
            for noeud, (x, y) in positions.items():
                # noeud
                c = plt.Circle((x, y), 0.1,color='lightblue')
                ax.add_patch(c)
                # Texte
                ax.text(x, y, str(noeud),
                    ha='center', va='center',
                    fontsize=12, fontweight='bold')

            # 3. Dessiner les ARCS 
            for source in self.noeuds:
                for cible in self.voisins.get(source, []):
                    x1, y1 = positions[source]
                    x2, y2 = positions[cible]
                    
                    # Flèche
                    ax.arrow(x1, y1, 
                            x2-x1, y2-y1,
                            head_width=0.03, 
                            head_length=0.05,
                            fc='gray', 
                            ec='gray',
                            length_includes_head=True,
                            alpha=0.7)

           
            
            # 4. Ajuster l'affichage
            ax.set_aspect('equal')  # Garde les proportions
            ax.axis('off')  # Cache les axes
    
            plt.show()

    #a changer
    def construction_graphe_majorite(self):
        self.Graphe = self.Graphe()

        # un candidat = un noeud
        for i in range(1,self.nb_candidats+1):
            self.Graphe.addNoeud(i)

        for i in range(1,self.nb_candidats +1): 
            for j in range(i+1,self.nb_candidats +1): 
                if self.matPref[i,j] > 0.5 * self.nb_votants :
                    self.Graphe.addVoisins(i,j)
                if self.matPref[i,j] < 0.5 * self.nb_votants :
                    self.Graphe.addVoisins(j,i)

def majority_trois_quarts_rec(inst, l_candidats, classement, essais=0):
    if not l_candidats:
        return 
    
    # aucun propre après un tour complet
    if essais >= inst.nb_candidats:
        classement.append(l_candidats)  # tous les restants sont sales
        return

    l_avant, l_apres, propre = inst.est_propre(l_candidats[0],l_candidats)

    if propre :
        majority_trois_quarts_rec(inst, l_avant,classement,essais+1)
        classement.append([l_candidats.pop(0)])
        majority_trois_quarts_rec(inst,l_apres,classement,essais+1)
    else : 
        l_candidats.append(l_candidats.pop(0)) #placer le candidat sale à la fin
        majority_trois_quarts_rec(inst,l_candidats,classement,essais+1)         


def majority_trois_quart(inst):
    classement = []
    majority_trois_quarts_rec(inst, list(inst.candidats.keys()),classement)
    return classement



# def majorite_trois_quart(inst):
#     classement =  dict() #cle= position et val = candidat ou instance reduite
            
#     for c in inst.candidats.keys():
#         if c not in [val for _,val in classement.items()]:
#             propre, l_avant, l_apres, paires_sales = inst.est_propre(c)

#             if propre :
#                 classement[len(l_avant)] = c #si propre -> 1 seul elt sinon plrs
#             else : 
#                 nv_inst = Instance()
#                 nv_inst.nb_votants = inst.nb_votants 
#                 nv_inst.nb_candidats = len(paires_sales)

#                 nv_inst.candidats = {k: inst.candidats[k] for k in paires_sales}

#                 nv_inst.matPref = copy.deepcopy(inst.matPref)

#                 nv_inst.init = True

#                 #on peut garder lui si on ne l'utilise nul part a part pour creer la matrice qui ne change pas ?
#                 nv_inst.profil_preferences = copy.deepcopy(inst.profil_preferences)

#                 classement[len(l_avant)] = nv_inst
#     return classement


# def majorite_trois_quart(inst):

#     l_propres = [] #candidats propres
#     l_sales = []
#     for c in inst.candidats.keys() : 
#         inst.est_propre(c,l_propres,l_sales)


#     classpropre =np.zeros(len(l_propres),dtype=int)
#     for c1 in l_propres :
#         pos = len(l_propres)-1
#         for c2 in l_propres[l_propres.index(c1):] : 
#             if c1!= c2 :
#                 if inst.matPref[c1,c2] > (3/4)*inst.nb_votants:
#                     pos -= 1
#         classpropre[pos] = c1

#     classementfinal = []
#     for i in range(len(classpropre)) :
#         tmp = set()
#         for c1 in l_sales :
#             if inst.matPref[c1,int(classpropre[i])] >= (3/4)*inst.nb_votants:
#                 tmp.add(c1)
#         for c in tmp :
#             l_sales.remove(c)
#         if tmp :
#             classementfinal.append(tmp)
#         classementfinal.append(int(classpropre[i]))

#     return classementfinal


def resolution_pl(inst) : 
    nbvar = inst.nb_candidats * (inst.nb_candidats - 1 )
    colonnes = range(nbvar)

    m = Model("Kemeny")

    # declaration variables de decision
    x = []
    for i in range(inst.nb_candidats):
        tmp = []
        for j in range(inst.nb_candidats):
            if i!=j :
                tmp.append(m.addVar(vtype=GRB.BINARY, name="x%d%d" %(i+1,j+1)))
        x.append(tmp) 

    #maj du modele pour integrer les nouvelles variables
    m.update()

    # pour tout (a,b) : xab + xba = 1
    for i in range(inst.nb_candidats):    
        for j in range(i+1,inst.nb_candidats):
            m.addConstr(x[i][j-1] + x[j][i] == 1) 

    # pour tout (a,b,c) : absence de cycle
    for i in range(inst.nb_candidats):    
        for j in range(i+1,inst.nb_candidats):
            for k in range(j+1,inst.nb_candidats):
                m.addConstr(x[i][j-1] + x[j][k-1] + x[k][i] >= 1) #xab + xbc + xca >= 1
                m.addConstr(x[i][k-1] + x[k][j] + x[j][i] >= 1) #xac + xcb + xba

    # Coefficients de la fonction objectif
    poids = inst.matPref

    #fonction obj : min somme(a,b) Qab · xba + Qba · xab
    obj = LinExpr()
    obj = 0

    for i in range(inst.nb_candidats):    
        for j in range(i+1,inst.nb_candidats):
            obj += x[j][i]*poids[i+1][j+1]  + x[i][j-1]*poids[j+1][i+1] 

    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)

    # Resolution du programme linéaire
    m.optimize()


    # Affichage de la solution 
    if m.status == GRB.OPTIMAL:
        print('\nSolution optimale:')
        position = dict()
        for v in m.getVars():
            print(f"{v.VarName} {v.X:g}") #:g pour avoir des int

            position[int(v.VarName[2])] = position.get(int(v.VarName[2]), 0) + int(v.X)

        print(position)
                
        print('\nValeur de la fonction objectif :', m.objVal)


#verifier init a chaque debut de fct !!!


i = Instance()
#i.lecture_fichier("00009-00000002.soc")
i.lecture_fichier("test.soc")
#i.lecture_fichier("majority.soc")
# print(i.candidats)
# print(i.nb_candidats)
# print(i.nb_votants)
# print(i.profil_preferences)
# print(i.score_Kemeny((1,3,2)))
# for c in range(1,i.nb_candidats+1):
#     print(c,i.est_propre(c))
#i.construction_graphe_majorite()
#print(i.Graphe.__str__())
#print(i.Graphe.get_CFC())
#i.Graphe.afficher_graphe()
# classement = majorite_trois_quart(i)
# print(classement)
# for cle in sorted(classement):
#     if type(classement[cle]) == int :
#         print(classement[cle], " > ", end='')
#     else : 
#         print(" { ", end='')
#         for c in classement[cle].candidats.keys():
#             print(c, " , ", end='')
#         print(" } > ", end='')
            

classm = majority_trois_quart(i)

resolution_pl(i)