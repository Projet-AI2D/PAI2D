# Problème de Kemeny : méthodes de décomposition et de résolution

La théorie du vote s’intéresse aux règles qui permettent de trouver un classement sur les candidats qui respecte les préférences individuelles. Parmi les méthodes existantes, l’agrégation de classements constitue un problème fondamental, avec des applications allant de l’apprentissage
automatique à la recherche web [1].

Parmi les règles de vote, la règle de Kemeny [2] établit un classement de consensus qui minimise
la distance totale de Kendall-tau définie comme le nombre total de désaccords (paires inversées)
entre le consensus et l’ensemble des préférences.

D’un point de vue théorique, la règle de Kemeny est la seule à respecter ces 3 propriétés : 

- le critère de Condorcet  
- l’axiome de renforcement
- la neutralité 


Problématique : sa solidité théorique est confrontée à une difficulté pratique majeure : sa
complexité. En effet, le calcul d’un classement de Kemeny est un problème NP-difficile [3, 4],
même lorsque le nombre de votants est fixé et petit, 4 par exemple [4].

Afin de répondre à cette problématique, des méthodes de décompositions ont été proposées. Ces
méthodes décomposent l’instance originale en de plus petits sous-problèmes indépendants qu’il
faudra ensuite résoudre.
Ce projet vise à implémenter des approches permettant de résoudre le problème de Kemeny
de manière exacte et efficace, même sur des instances de grande taille.

## Dépendances 

Toutes les bibliothèques nécessaires peuvent être installées via la commande : 

``` pip install -r requirements.txt ```

Une licence Gurobi est nécessaire pour la programmation linéaire.

## Structure du projet

* dossier *dataset* :  
Il contient toutes les instances réelles d'ordre strict et complet de PrefLib ( [lien vers le dépôt PrefLib](https://github.com/PrefLib/PrefLib-Data/blob/main/datasets/00009%20-%20agh/00009-00000002.soc) ) 

* *instance.py* :  
 Il contient les méthodes de lecture d'instance PrefLib, les méthodes de décomposition et de résolution.

* *eval.py* : 
Il contient les fonctions d'évaluation du temps d'execution et des décompositions. 

* dossier *top-k-mallows* : 
Il contient les fichiers de code récupéré sur github ( [lien vers le dépôt top-k-mallows](https://github.com/ekhiru/top-k-mallows.git) ) permettant de générer des profils de préférences avec le modèle de mallows.

* *generation_instance* :
Il contient la méthode pour générer une instance à l'aide du modèle de Mallows et les méthodes d'évaluation des décompositions et de la programmation linéaire sur les instance générées.

* *projet.ipynb* :  
Ce notebook permet de tester nos fonctions les plus importantes sur la petite instance du fichier *exemple.soc*

Tous les résultats sont stockés dans des fichiers csv. 

## Références 

[1] Dwork Cynthia, Kumar Ravi, Moni Naor, and D. Sivakumar. Rank aggregation methods
for the web. 2001

[2] Kemeny John G. Mathematics without numbers. 1959

[3] Nadja Betzler, Robert Bredereck, and Rolf Niedermeier. Theoretical and empirical evalua-
tion of data reduction for exact kemeny rank aggregation. 2013

[4] Fischer Felix, Hudry Olivier, and Niedermeier Rolf. Weighted tournament solutions. 2016