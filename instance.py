import numpy as np
import copy
from gurobipy import *
from itertools import combinations
import time 
from preflibtools.instances import OrdinalInstance
import matplotlib.pyplot as plt
import networkx as nx

class Instance :
    """ 
        Représente une instance de problème de vote

        Attributs : 
        ----------
        nb_votants: int 
            nombre de votants
        nb_candidats: int
            nombre de candidats
        candidats: dictionnaire
            clé : indice du candidats , valeur : nom du candidat
        matPref: np.ndarray
            matrice des préférences (matPref[i,j] = nombre de votants préférant i à j)
        graphe: Graphe (classe interne) 
            graphe de majorité
        init: booléen
            indique si l'instance est initialisée
    """ 

    def __init__ (self) :
        """ Initialise une instance vide"""
        self.init = False 
        self.graphe = None
        self.matPef = None
    
    def __str__(self):
        return f"Instance({list(self.candidats.keys())})"

    # pouvoir afficher l'instance dans le classement (liste)
        def __repr__(self):
            return self.__str__()
        
    def lecture_fichier(self,nomfich):
        """ 
            Lit un fichier contenant une instance (de Preflib) et initialise l'instance
        
            Paramètres
            ----------
            nomfich: chemin du fichier contenant l'instance à lire
        
            Sortie
            -------
            temps : temps de création de la matrice de preferences
        """

        if self.init : #deja initialisé
            return 

        inst = OrdinalInstance() 
        inst.parse_file(nomfich) #lecture de l'instance dans le fichier

        self.nb_votants = inst.num_voters # nombre de votants
        self.nb_candidats = inst.num_alternatives    # nombre de candidats
        self.candidats =  inst.alternatives_name   # dictionnaire cle=indice , valeur = nom du candidat
        
        profil_preferences = {tuple(x[0] for x in k): v for k, v in inst.multiplicity.items()} #dictionnaire cle = classements et valeur = nombre d'apparition
        self.init = True

        start = time.process_time()
        self.comptage(profil_preferences) #création de la matrice de préférences
        end = time.process_time()
        temps = end - start #temps de création de la matrice de preferences

        return temps
    
    def comptage(self, profil) : 
        """ 
            Construit la matrice des préférences à partir du profil de préférences
        
            Paramètres
            ----------
            profil: profil de préférences
        
            Sortie
            -------
            aucune sortie
        """
        #si l'instance est initialisée on ne reconstruit pas la matrice
        if not self.init :
            raise Exception("Initialisez l'instance avec lecture_fichier")

        #si la matrice est initialisée on ne reconstruit pas la matrice
        if self.matPef is not None : 
            return

        #matPref[i,j] = nb de votants qui preferent i à j, la premiere ligne et premiere colonne sont vides pour concorder avec les indices
        self.matPref = np.zeros((self.nb_candidats+1,self.nb_candidats+1)) 
        for pref, nbpref in profil.items() :
            for i in range(1,self.nb_candidats+1) : 
                for j in range(i+1, self.nb_candidats+1) : 
                    if pref.index(i) < pref.index(j): #la position des candidats 
                        self.matPref[i,j] += nbpref
                    else : 
                        self.matPref[j,i] += nbpref        
       
    def est_propre(self,cand,candidats) :
        """ 
            Determine si un candidat est "propre" (dominance à 3/4)
        
            Paramètres
            ----------
            cand: le candidat à tester
            candidats: liste 
                liste des candiats restants 
                                
            Sortie
            -------
            (l_avant, l_apres,propre) : (liste,liste,propre)
                - les candidats préférés à cand (classés avant)
                - les candidats non préférés à cand (classés après)
                - si cand est propre
        """

        if not self.init : #si l'instance n'est pas initialisée on ne peut vérifier si un candidat est propre
            raise Exception("Initialisez l'instance avec lecture_fichier")

        l_avant = []
        l_apres = []
        propre = True
        for i in candidats : 
            if i == cand : #on ne compare pas un candidat avec lui même
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
        """ 
            Représente un graphe orienté de majorité
        
            Attributs : 
            ----------
            noeuds: liste 
                liste des noeuds (candidats)
            voisins: dictionnaire d'adjacence
                clé : noeud , valeur : liste des voisins
        """

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
            """ Ajoute un noeud cand et on lui initialise sa liste de voisins à vide """
            if cand not in self.noeuds:
                self.noeuds.append(cand)
                self.voisins[cand]=[]

        def addVoisins(self,cand1,cand2):
            """ Ajoute un arc orienté d'un candidat cand1 vers un candidat cand2 """
            # S'assurer que les noeuds existent
            self.addNoeud(cand1)
            self.addNoeud(cand2)
            
            if cand2 not in self.voisins[cand1]:
                self.voisins[cand1].append(cand2)

        def getVoisins(self,cand):  
            return self.voisins.get(cand,[]) #[] valeur par defaut
            

        def afficher_graphe(self):
            """ Affiche le graphe """
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
        """ 
            Construire le graphe de majorité à partir de la matrice de préférences. 
            Chaque candidat est un noeud et il y a un arc orienté de i vers j si une majorité stricte préfère i à j (>50%)
        """
        if not self.init : #si l'instance n'est pas initialisée on ne peut construire de graphe de majorité
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


def majorite_trois_quarts_rec(inst, l_candidats,classement):
    """ 
        Algorithme récursif de classement basé sur la majorité des 3/4
    
        Paramètres
        ----------
        inst: object Instance
            l'instance du problème
        l_candidats: liste 
            liste des candiats restants 
        classement: liste
            classement en construction

        Sortie
        -------
        aucune sortie
    """
    i=0
    while i < len(l_candidats):
        l_avant, l_apres, propre = inst.est_propre(l_candidats[i],l_candidats)
        if propre : 
            majorite_trois_quarts_rec(inst, l_avant,classement)
            classement.append(l_candidats.pop(i)) #ajout du candidat propre à la bonne position dans le classement et le supprimer des candidats restants
            majorite_trois_quarts_rec(inst,l_apres,classement) 
            return 
        else :
            i = i +1 
    
    #création d'une sous-instance
    nv_inst = Instance() 
    nv_inst.nb_votants = inst.nb_votants 

    #uniquement les candidats restants
    nv_inst.nb_candidats = len(l_candidats) 
    nv_inst.candidats = {k: inst.candidats[k] for k in l_candidats}

    nv_inst.matPref = copy.deepcopy(inst.matPref) # matrice de préférences identiques
    nv_inst.init = True

    #ajout de l'instance à la bonne position dans le classement
    classement.append(nv_inst)  # tous les restants sont des candidats non propres 
    return



def majorite_trois_quart(inst):
    """ 
        Lance l'algorithme de classement par majorité des 3/4
    
        Paramètres
        ----------
        inst: object Instance
            l'instance du problème

        Sortie
        -------
        classement: liste
            contient les candidats fixés et les sous-instances classés selon la règle de majorité des 3/4
    """

    if inst is None : 
        raise Exception("Créer l'instance")

    if not inst.init : #si l'instance n'est pas initialisée on ne peut appliquer la règle de majorité des 3/4
            raise Exception("Initialisez l'instance avec lecture_fichier")

    classement = []
    majorite_trois_quarts_rec(inst, list(inst.candidats.keys()),classement)
    return classement


def condorcet_etendu(inst) : 
    """ 
        Décompose l'instance en sous-instance(s) en ordonnant les composantes fortement connexes dans le graphe de majorité à l'aide de l'algorithme de Tarjan
    
        Paramètres
        ----------
        inst: object Instance
            l'instance du problème
                            
        Sortie
        -------
        classement: liste
            contient les candidats fixés et les sous-instances classés selon le critère de condorcet étendu
    """
    if inst is None : 
        raise Exception("Créer l'instance")

    if not inst.init : #si l'instance n'est pas initialisée on ne peut appliquer le critère de condorcet étendu
            raise Exception("Initialisez l'instance avec lecture_fichier")

    if inst.graphe is None:
        inst.construction_graphe_majorite()

    num = 0
    pile = []
    partition = []

    numAccessible = {}# dict : clé : noeud (candidat) , valeur : place du sommet accessible le plus bas dans la pile
    numero = {}# dict : clé : noeud (candidat) , valeur : sa place dans la pile

    def Tarjan(sommetInit):
        nonlocal num, pile, partition,numAccessible,numero  # Déclare que ces variables viennent de la fonction parente
        pile.append(sommetInit) 
        numAccessible[sommetInit] = num 
        numero[sommetInit] = num 
        num += 1 

        for voisin in inst.graphe.getVoisins(sommetInit) : 
            if voisin not in numero: #si voisin n'est pas dans la pile
                Tarjan(voisin)
                #on met a jour le sommet accessible le plus bas 
                numAccessible[sommetInit] = min(numAccessible[sommetInit],numAccessible[voisin])
                
            elif voisin in pile:
                numAccessible[sommetInit] = min(numAccessible[sommetInit],numero[voisin])
                
        if numAccessible[sommetInit] == numero[sommetInit] : 
            #après avoir visité tous les sommets voisins (directs et indirects), si le noeud est le noeud le plus bas accessible alors on a fait le tour de cette composante fortement connexe
            cfc = set()
            w = pile.pop()
            while w != sommetInit :
                cfc.add(w)
                w = pile.pop()
            cfc.add(w)

            if len(cfc) > 1 : #sous-instance
                #création d'une sous-instance
                nv_inst = Instance()
                nv_inst.nb_votants = inst.nb_votants 

                #uniquement les candidats de la même composante fortement connexe
                nv_inst.nb_candidats = len(cfc)
                nv_inst.candidats = {k: inst.candidats[k] for k in cfc}

                nv_inst.matPref = copy.deepcopy(inst.matPref) # matrice de préférences identiques
                nv_inst.init = True

                #ajout de l'instance à la bonne position dans le classement
                partition.insert(0,nv_inst) #inserer l'instance en tête 

            else :
                partition.insert(0,cfc.pop())  #ajout du candidat à la bonne position dans le classement 
    
    for n in inst.graphe.noeuds : 
        if n not in numAccessible.keys(): #si le noeud n'est dans aucune cfc (noeud isolé par exemple)
            Tarjan(n)

    return partition

def resolution_pl(inst) : 
    """ 
        Résout le problèùe de classement de Kemeny via programmation linéaire 
    
        Paramètres
        ----------
        inst: object Instance
            l'instance du problème

        Varaibles
        ----------
        x[i][j] = 1 si le candidat i est classé avant le candidat j

        Contraintes
        -----------
            - antisymetrie (i avant j ou j avant i)
            - absence de cycles
       
        Sortie
        -------
        m: modèle Gurobi 
    """

    m = Model("Kemeny")
    candidats = list(inst.candidats.keys())

    # declaration variables de decision
    x = []
    for i in candidats:
        tmp = []
        for j in candidats:
            if i!=j : #on ne compare pas un candidat avec lui même
                tmp.append(m.addVar(vtype=GRB.BINARY, name="x_%d_%d" %(i,j)))
        x.append(tmp) 

    #mise a jour du modele pour integrer les nouvelles variables
    m.update()

    # pour tout (i,j) : xij + xji = 1
    for i in range(inst.nb_candidats):    
        for j in range(i+1,inst.nb_candidats):
            m.addConstr(x[i][j-1] + x[j][i] == 1) 

    # pour tout (i,j,k) : absence de cycle
    for i in range(inst.nb_candidats):    
        for j in range(i+1,inst.nb_candidats):
            for k in range(j+1,inst.nb_candidats):
                m.addConstr(x[i][j-1] + x[j][k-1] + x[k][i] >= 1) #xij + xjk + xki >= 1
                m.addConstr(x[i][k-1] + x[k][j] + x[j][i] >= 1) #xik + xkj + xji >= 1

    # Coefficients de la fonction objectif
    poids = inst.matPref

    #fonction obj : min somme(i,j) Qij · xji + Qji · xij
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
    """ 
        Reconstruit le classement des candidats à partir du modèle Gurobi "modele" 
        On calcule pour chaque candidat sa position en sommant la valeur des xij correspondants
    
        Paramètres
        ----------
        modele: modèle Gurobi après résolution
        inst: Objet Instance
            l'instance du problème
       
        Sortie
        -------
        classement: liste
            classement des candidats après résolution par programmation linéire
    """
    if modele.status == GRB.OPTIMAL: #s'il existe une solution
        position = dict()
        classement = np.zeros(inst.nb_candidats, dtype=int)
        #calcul de la position de chaque candidat
        for v in modele.getVars():
            #print(f"{v.VarName} {v.X:g}") #:g pour avoir des int
            i , j = v.VarName[2:].split("_")
            position[int(j)] = position.get(int(j), 0) + int(v.X)
            
        #reconstruction du classement final
        for v in modele.getVars():
            classement[position[int(j)]] = int(j)
        return list(classement)

    raise Exception ("Il n'existe pas de solution")
        

def score_Kemeny(matPref, classement) : 
    """
        Calcule le score de Kemeny (distance de Kendall Tau)
        
        Paramètres
        ----------
        matPref: matrice de préférences
        classement: ordre des candidats
       
        Sortie
        -------
        score: int
            score de Kemeny
    """ 
    score=0
    for i in classement :
        for j in classement[classement.index(i)+1:] :
            score += matPref[j,i]
    return score


def resolution_dyn(inst):
    """ 
        Résout le problèùe de classement de Kemeny via programmation dynamique 
        On calcule le score minimal pour chaque sous-ensemble de candidats, on mémorise le candidat en tête et le score minimal associé
    
        Paramètres
        ----------
        inst: object Instance
            l'instance du problème
       
        Sortie
        -------
        c_opti: dictionnaire 
            cle : ensemble candidat ordonné dans l'ordre croissant de leur numero , valeur : (candidat en tête, score)
    """

    c_opti = dict()
    
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

                    if score_min > score_reste + cout_cand : #si le score avec cand en tête est meilleur 
                        score_min = score_reste + cout_cand 
                        cand_en_tete = cand

                c_opti[c] = (cand_en_tete,int(score_min))
            
    return c_opti

def reconstruction_classement_PDyn(c_opti,inst):
    """ Reconstruit le classement final a partir du dictionnaire obtenu par resolution de programmation dynamique.

    Paramètres
    ----------
    c_opti: dict()
        Le dictionnaire associe à un ensemble de candidats ordonnés, le couple (candidat en tete, score).
    inst: Instance
        Instance à résoudre.

    Sortie
    -------
    list
        Le classement final reconstitué.
    """ 
    classement = []
    c = tuple(sorted(inst.candidats.keys())) #tous les candidats triés dans l'ordre croissant de leur identifiant
    for t in range(inst.nb_candidats):
        classement.append(c_opti[c][0]) #ajout du candidat en tête 
        c = tuple(x for x in c if x != c_opti[c][0]) #candidat déja classé
    return classement

def cout(cand , l_candidats, matPref):
    """ Calcule le coût de placer un candidat en tête d'un ensemble de candidats.

    Paramètres
    ----------
    cand : int
        L'identifiant du candidat que l'on place en première position.
    l_candidats : tuple of int
        L'ensemble des candidats (sous forme de tuple immuable) par rapport 
        auxquels on calcule le coût.
    matPref : np.ndarray
        La matrice des préférences.

    Sortie
    -------
    int
        Le coût total cumulé (somme des désaccords) pour ce placement.
    """ 
    somme = 0
    for c in l_candidats : 
        somme += matPref[c,cand] #nombre de désaccords
    return somme


def resolution(inst, fct_resolution, fct_reconstruction, reduction1=None, reduction2=None) : 
    """ Résout complètement une instance en appliquant optionnellement des réductions.

    Paramètres
    ----------
    inst: Instance
        Instance à résoudre.
    fct_resolution: callable
        Methode de résolution utilisée (resolution_pl ou resolution_dyn)
    fct_reconstruction: callable
        Fonction permettant de reconstruire le classement obtenu après résolution (reconstruction_classement_PL ou reconstruction_classement_PDyn)
    reduction1: callable, optional
        Première méthode de réduction (condorcet_etendu ou majorite_trois_quart). Par défaut None.
    reduction2: callable,optional
        Deuxième méthode de réduction pour combinaison (condorcet_etendu ou majorite_trois_quart). Par défaut None.

    Sorties
    -------
    float
        Temps d'execution total en secondes.
    list
        Classement final obtenu après résolution et reconstruction
    """
    
    inst_reduite = [] #liste contenant dans l'ordre les candidats fixés et les sous instances à traiter
    temps = 0

    if reduction1 is not None : #première réduction
        start = time.process_time()
        red1 = reduction1(inst) #résultat de la premiere réduction
        end = time.process_time()
        temps += end - start #temps d'execution de la réduction

        if reduction2 is not None : #combiner 3/4 et condorcet
            for i in red1 : 
                if type(i) == Instance: #on réduit les sous instances 
                    
                    start = time.process_time()
                    red2 = reduction2(i) #résultat de la premiere réduction
                    end = time.process_time()
                    temps += end - start #temps d'execution des deux réductions
                    
                    inst_reduite += red2

                else : 
                    inst_reduite.append(i)
        
        else : #une seule réduction
            inst_reduite = red1
                

    else : #pas de reduction 
        inst_reduite.append(inst)

    classement = [] #classement final des candidats 
    for i in inst_reduite:
        if type(i) == Instance: #resoudre les sous instances 
            
            start = time.process_time()
            res = fct_resolution(i)
            end = time.process_time()
            temps += end - start #ajout du temps de resolution d'une sous instance
            
            classement += fct_reconstruction(res,i) #reconstruction du classement a partir de la solution obtenu 

        else : 
            classement.append(i)        

    return temps, classement


#verifier init a chaque debut de fct !!! 
#ajouter fct affichage d'instance
#on doit tous reverifier pour que les numero soit associe au bon cand 
# car on est pati du principe que c'etait des entier !!

if __name__ == "__main__":
    i = Instance()
    i.lecture_fichier("exemple.soc")
    print(f'candidats : {i.candidats}\n nombre de candidats : {i.nb_candidats} \n nombre de votants : {i.nb_votants} \n')

    for c in range(1,i.nb_candidats+1):
        _,_, p = i.est_propre(c,list(i.candidats.keys()))
        if p :
            print(f'{c} est propre')
        else :
            print(f'{c} est non propre')

    classement_trois_quart = majorite_trois_quart(i)
    print(f'reduction par 3/4 : {classement_trois_quart} \n')
        
    classement_CCE = condorcet_etendu(i)        
    print(f'reduction par CCE : {classement_CCE} \n')

    m = resolution_pl(i)
    classement_PL = reconstruction_classement_PL(m,i)
    print(f'resolution par PL : {np.array2string(np.array(classement_PL), separator=" > ")}')
    print(f'score de Kemeny : {score_Kemeny(i.matPref,classement_PL)} \n')

    m = resolution_dyn(i)
    classement_Dyn = reconstruction_classement_PDyn(m,i)
    print(f'resolution par PDyn : {np.array2string(np.array(classement_Dyn), separator=" > ")} \n')
    print(f'score de Kemeny : {score_Kemeny(i.matPref,classement_Dyn)} \n')




   