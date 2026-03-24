import numpy as np
import copy
from gurobipy import *
from itertools import combinations
import time 

from preflibtools.instances import OrdinalInstance

import matplotlib.pyplot as plt
import networkx as nx

class Instance :
    def __init__ (self) :
        self.init = False 
        self.graphe = None
        self.matPef = None
    
    def lecture_fichier(self,nomfich):
        if self.init : #deja initialisé
            return 
        inst = OrdinalInstance() 
        inst.parse_file(nomfich) #lecture de l'instance dans le fichier

        self.nb_votants = inst.num_voters # nombre de votants
        self.nb_candidats = inst.num_alternatives    # nombre d'alternatives
        self.candidats =  inst.alternatives_name   # dictionnaire cle=indice , valeur = nom alternative
        
        profil_preferences = {tuple(x[0] for x in k): v for k, v in inst.multiplicity.items()} #dictionnaire cle = classements et valeur = nombre d'apparition
        self.init = True
        self.comptage(profil_preferences)

    
    def comptage(self, profil) : 
        if not self.init :
            raise Exception("Initialisez l'instance avec lecture_fichier")

        if self.matPef is not None : 
            return

        self.matPref = np.zeros((self.nb_candidats+1,self.nb_candidats+1)) #matPref[i,j] = nb de votants qui preferent i à j, la premiere ligne et premiere colonnes sont vides pr avoir les bon indices
        for pref, nbpref in profil.items() :
            for i in range(1,self.nb_candidats+1) : 
                for j in range(i+1, self.nb_candidats+1) : 
                    if pref.index(i) < pref.index(j):
                        self.matPref[i,j] += nbpref
                    else : 
                        self.matPref[j,i] += nbpref        


    def est_propre2(self,cand,candidats) :
        if not self.init :
            raise Exception("Initialisez l'instance avec lecture_fichier")

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

        def getVoisins(self,cand):#recuperer les voisins    
            return self.voisins.get(cand,[]) #[] valeur par defaut
            

        def afficher_graphe(self):
            G = nx.DiGraph() #graphe orienté 
            G.add_nodes_from(self.noeuds) #ajout des noeuds

            for source,voisins in self.voisins.items():
                for v in voisins :
                    G.add_edge(source,v)
            
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(G)

            nx.draw(G,pos,with_labels=True,node_color='lightblue',node_size=500)
            plt.show()
                

    def construction_graphe_majorite(self):
        if not self.init :
            raise Exception("Initialisez l'instance avec lecture_fichier")

        self.graphe = self.Graphe()
        candidats = list(self.candidats.keys())

        # un candidat = un noeud
        for i in candidats:
            self.graphe.addNoeud(i)

        for i in range(self.nb_candidats): 
            for j in range(i+1,self.nb_candidats): 
                if self.matPref[candidats[i],candidats[j]] > 0.5 * self.nb_votants :
                    self.graphe.addVoisins(candidats[i],candidats[j])
                if self.matPref[candidats[i],candidats[j]] < 0.5 * self.nb_votants :
                    self.graphe.addVoisins(candidats[j],candidats[i])

        
def majority_trois_quarts_rec(inst, l_candidats, classement, essais=0):
    if not l_candidats:
        return 
    
    # aucun propre après un tour complet
    if essais >= inst.nb_candidats:
        nv_inst = Instance()
        nv_inst.nb_votants = inst.nb_votants 
        nv_inst.nb_candidats = len(l_candidats)
        nv_inst.candidats = {k: inst.candidats[k] for k in l_candidats}
        nv_inst.matPref = copy.deepcopy(inst.matPref)
        nv_inst.init = True
        classement.append(nv_inst)  # tous les restants sont sales
        return

    l_avant, l_apres, propre = inst.est_propre2(l_candidats[0],l_candidats)

    if propre :
        majority_trois_quarts_rec(inst, l_avant,classement,essais+1)
        classement.append(l_candidats.pop(0))
        majority_trois_quarts_rec(inst,l_apres,classement,essais+1)
    else : 
        l_candidats.append(l_candidats.pop(0)) #placer le candidat sale à la fin
        majority_trois_quarts_rec(inst,l_candidats,classement,essais+1)         


def majority_trois_quart(inst):
    classement = []
    majority_trois_quarts_rec(inst, list(inst.candidats.keys()),classement)
    return classement


def condorcet_etendu(inst) : 
    if inst.graphe is None:
        inst.construction_graphe_majorite()

    num = 0
    pile = []
    partition = []

    numAccessible = {}
    numero = {}

    def DFS_recursif(sommetInit):
        nonlocal num, pile, partition,numAccessible,numero  # Déclare que ces variables viennent de la fonction parente
        pile.append(sommetInit) #noeud + lowlink
        numAccessible[sommetInit] = num #place du sommet accessible le plus bas dans la pile
        numero[sommetInit] = num #place dans la pile
        num += 1 

        for voisin in inst.graphe.getVoisins(sommetInit) : 
            if voisin not in numero:
                DFS_recursif(voisin)
                numAccessible[sommetInit] = min(numAccessible[sommetInit],numAccessible[voisin])
                
            elif voisin in pile:
                numAccessible[sommetInit] = min(numAccessible[sommetInit],numero[voisin])
                
        if numAccessible[sommetInit] == numero[sommetInit] : 
            cfc = set()
            w = pile.pop()
            while w != sommetInit :
                cfc.add(w)
                w = pile.pop()
            cfc.add(w)

            if len(cfc) > 1 :
                nv_inst = Instance()
                nv_inst.nb_votants = inst.nb_votants 
                nv_inst.nb_candidats = len(cfc)
                nv_inst.candidats = {k: inst.candidats[k] for k in cfc}
                nv_inst.matPref = copy.deepcopy(inst.matPref)
                nv_inst.init = True

                partition.insert(0,nv_inst) #inserer l'instance en tête 
            else :
                partition.insert(0,cfc.pop())  
    
    for n in inst.graphe.noeuds : 
        if n not in numAccessible.keys(): #si le noeud n'est dans aucune cfc (noeud isolé par exemple)
            DFS_recursif(n)

    return partition



def resolution_pl(inst) : 

    m = Model("Kemeny")

    # declaration variables de decision
    x = []
    candidats = list(inst.candidats.keys())
    for i in candidats:
        tmp = []
        for j in candidats:
            if i!=j :
                tmp.append(m.addVar(vtype=GRB.BINARY, name="x%d%d" %(i,j)))
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
            obj += x[j][i]*poids[candidats[i]][candidats[j]]  + x[i][j-1]*poids[candidats[j]][candidats[i]]

    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)

    # Resolution du programme linéaire
    m.optimize()

    # Affichage de la solution 
    #if m.status == GRB.OPTIMAL:               
        #print('\nValeur de la fonction objectif :', m.objVal)
    
    return m 

def reconstruction_classement_PL(modele,inst):
    if modele.status == GRB.OPTIMAL:
        position = dict()
        classement = np.zeros(inst.nb_candidats, dtype=int)
        for v in modele.getVars():
            #print(f"{v.VarName} {v.X:g}") #:g pour avoir des int
            position[int(v.VarName[2:])] = position.get(int(v.VarName[2:]), 0) + int(v.X)

        for v in modele.getVars():
            classement[position[int(v.VarName[2:])]] = int(v.VarName[2:])
        return list(classement)
    raise Exception ("Il n'existe pas de solution")
        

#somme des dist de Kendall Tau
def score_Kemeny(matPref, classement) : 
    score=0
    for i in classement :
        for j in classement[classement.index(i)+1:] :
            score += matPref[j,i]
    return score


def resolution_dyn(inst):
    
    c_opti = dict() #key = ensemble candidat ordonné dans l'ordre croissant de leur numero
                    #valeur = (candidat en tête, score)
    
    for t in range(1,inst.nb_candidats+1): #taille sous-ensemble
        for c in combinations(sorted(inst.candidats.keys()),t): #combinaison possible 
            print("candidats : ",c)
            if t == 1 :
                c_opti[c] = (c[0],0)
            else : 
                score_min = np.inf
                cand_en_tete = c[0]
                for cand in c : #on test chaque candidat en tête 

                    reste = tuple(x for x in c if x != cand)
                    score_reste = c_opti[reste][1]
                    cout_cand = cout(cand,reste,inst.matPref)

                    if score_min > score_reste + cout_cand : 
                        score_min = score_reste + cout_cand 
                        cand_en_tete = cand

                c_opti[c] = (cand_en_tete,int(score_min))
            
    return c_opti

def reconstruction_classement_PDyn(c_opti,inst):
    classement = []
    #tous les candidats triés dans l'ordre croissant de leur numero
    c = tuple(sorted(inst.candidats.keys())) 
    for t in range(inst.nb_candidats):
        classement.append(c_opti[c][0])
        c = tuple(x for x in c if x != c_opti[c][0])
    
    return classement

#cout de placer cand en tête de l_candidats
def cout(cand , l_candidats, matPref):
    somme = 0
    for c in l_candidats : 
        somme += matPref[c,cand] #cout de placer cand avant c 
    return somme

def resolution(inst, fct_resolution, fct_reconstruction, reduction1=None, reduction2=None) : 
    
    inst_reduite = []
    temps = 0

    if reduction1 is not None :
        start = time.process_time()
        
        red1 = reduction1(inst)
        
        end = time.process_time()
        temps += end - start

        if reduction2 is not None : #combiner 3/4 et condorcet
            for i in red1 : 
                if type(i) == Instance:
                    start = time.process_time()
                    
                    red2 = reduction2(i)
                    
                    end = time.process_time()
                    temps += end - start
                    
                    inst_reduite += red2
                else : 
                    inst_reduite.append(i)
        else : 
            inst_reduite = red1
                

    else :
        inst_reduite.append(inst)

    classement = []
    for i in inst_reduite:
        if type(i) == Instance:
            start = time.process_time()
            
            res = fct_resolution(i)
            
            end = time.process_time()
            temps += end - start
            
            classement += fct_reconstruction(res,i)
        else : 
            classement.append(i)        

    return temps, classement


#verifier init a chaque debut de fct !!! 
#ajouter fct affichage d'instance
#on doit tous reverifier pour que les numero soit associe au bon cand 
# car on est pati du principe que c'etait des entier !!


# i = Instance()
# i.lecture_fichier("datasets/00011 - web/00011-00000003.soc")
# #i.lecture_fichier("test.soc")
# i.lecture_fichier("majority.soc")
# # print(i.candidats)
# # print(i.nb_candidats)
# # print(i.nb_votants)
# # print(i.profil_preferences)
# # print(i.score_Kemeny((1,3,2)))
# # for c in range(1,i.nb_candidats+1):
# #     print(c,i.est_propre(c))
# i.construction_graphe_majorite()
# # print(i.graphe.__str__())


#classement = majorite_trois_quart(i)
# # print(classement)
# # for cle in sorted(classement):
# #     if type(classement[cle]) == int :
# #         print(classement[cle], " > ", end='')
# #     else : 
# #         print(" { ", end='')
# #         for c in classement[cle].candidats.keys():
# #             print(c, " , ", end='')
# #         print(" } > ", end='')
# classmCondorcet = condorcet_etendu(i)        
# print(classmCondorcet)
#classm = majority_trois_quart(i)
# print(classm)
# #print(score_Kemeny(i.matPref,classmCondorcet))
# # i.graphe.afficher_graphe()
# m = resolution_pl(i)
# print(np.array2string(reconstruction_classement_PL(m,i), separator=' > '))
# #print( " recPL : ",reconstruction_classement_PL(m,i))
# classmdyn = resolution_dyn(i)
# #print(np.array2string(reconstruction_classement_PDyn(classmdyn,i), separator=' > '))
# print( " recPDyn : ",reconstruction_classement_PDyn(classmdyn,i))
# # print(classmdyn)
# # print(score_Kemeny(i.matPref,classmdyn))

# print(classement)
# print(classm)
