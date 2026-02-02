import numpy as np
from preflibtools.instances import OrdinalInstance 





class Instance :
    def __init__ (self) :
        self.init = False 
    

    # NUMBER ALTERNATIVES: 7
    # NUMBER VOTERS: 153
    def lecture_fichier(self,nomfich):
        inst = OrdinalInstance() 
        inst.parse_file(nomfich) #lecture de l'instance dans le fichier

        self.nb_votants = inst.num_voters # nombre de votants
        self.nb_candidats = inst.num_alternatives    # nombre d'alternatives
        self.candidats =  inst.alternatives_name   # dictionnaire cle=indice , valeur = nom alternative
        
        self.profil_preferences = {tuple(x[0] for x in k): v for k, v in inst.multiplicity.items()} #dictionnaire cle = classements et valeur = nombre d'apparition
        self.init = True
        self.comptage(self.profil_preferences)

    def comptage(self, profil) : 
        #si on garde pas le profil de preference on doit refaire ca ici : profil = {tuple(x[0] for x in k): v for k, v in inst.multiplicity.items()} 
        
        self.matPref = np.zeros((self.nb_candidats,self.nb_candidats)) #matPref[i,j] = nb de votants qui preferent i à j
        for pref, nbpref in profil.items() :
            for i in range(1,self.nb_candidats+1) : 
                for j in range(i+1, self.nb_candidats+1) : 
                    if pref.index(i) < pref.index(j):
                        self.matPref[i-1,j-1] += nbpref
                    else : 
                        self.matPref[j-1,i-1] += nbpref
        
#  def Kendall_Tau(classement1, classement2) : 
#     distance=0
#     for i in range(len(classement1)) : 
#         cand = classement1[i]
#         i2 = classement2.index(cand)
#         distance += min(np.abs(i - i2) , np.abs(i - i2-1) ) 
        
#     return distance

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
                score += self.matPref[j-1,i-1]
        return score

        


    def est_propre(self,cand) : 
        for i in range(self.nb_candidats) : 
            if self.matPref[cand,i] < (3/4)*self.nb_votants or self.matPref[cand,i] > (3/4)*self.nb_votants : 
                return True
        return False
            

i = Instance()
#i.lecture_fichier("00009-00000002.soc")
i.lecture_fichier("test.soc")
print(i.candidats)
print(i.nb_candidats)
print(i.nb_votants)
print(i.profil_preferences)
print(i.score_Kemeny((1,3,2)))
