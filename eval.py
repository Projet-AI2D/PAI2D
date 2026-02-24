import instance 



red = [instance.majority_trois_quart, instance.condorcet_etendu]
res = [instance.resolution_dyn, instance.resolution_pl]
rec = [instance.reconstruction_classement_PDyn, instance.reconstruction_classement_PL]


def eval_temps(nomfich,fichDest="eval_temps.txt") : 
    
    f = open(fichDest,'a')
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich)+ ' ')
    f.write(str(inst.nb_candidats) + ' ')

    for rs in range(len(res)) : 
        for rd in red :
            f.write(str(instance.resolution(inst, res[rs], rec[rs], rd)[0]) + ' ') #avec une réduction
        f.write(str(instance.resolution(inst, res[rs], rec[rs], red[0],red[1])[0]) + ' ' )#3/4 puis condorcet
        f.write(str(instance.resolution(inst, res[rs], rec[rs],red[1],red[0])[0]) + ' ' )#condorcet puis 3/4  
        f.write(str(instance.resolution(inst, res[rs],rec[rs])[0]) + ' ') #sans reduction
    # print(nomfich)
    # f.write(str(instance.resolution(inst, res[0],rec[0],red[0])[0]) + ' ') #sans reduction

    f.write('\n')
    
    f.close()

#eval_temps("test.soc")


def eval_reduction(nomfich,fichDest="eval_reduction.txt"): 
    f = open(fichDest,'a')
    inst = instance.Instance()
    inst.lecture_fichier(nomfich)

    f.write(os.path.basename(nomfich) + ' ')
    f.write(str(inst.nb_candidats) + ' ')

    for rd in red :
        nbmax = 0 
        nb_fixes =0
        classement = rd(inst)
        for i in classement : 
            if type(i) == instance.Instance:
                nbmax = max(nbmax,i.nb_candidats)
            else : 
                nb_fixes +=1
        f.write(str(nbmax)+ ' ' + str(nb_fixes) + ' ')

    f.write('\n')
    
    f.close()

#eval_reduction("test.soc")

import os

def eval_allFiles(dataset="00004 - netflix"): 
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

eval_allFiles("00006 - skate")
            



