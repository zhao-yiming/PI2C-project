# PI2C-project
IA qui répond au request du Server, si le request est 'subscribe' alors il renvoie une requête d'iscription. Si le requet est 'play', il calculera le coup favorable à jouer par la méthode de negamaxWithPruningIterativeDeepening

# démarrer l'IA client abalone

il faut d'abord lancer le Server du jeu abalone et ensuite lancer ce programme en lui fournissant un port dans la commande, ce programme peut reçevoir seulement un port pour démarrer.
si on souhaite qu'il s'affronte contre lui même, il faut lancer ce programme dans des fenêtres de commandes différent

# calcul des mouvements possibles

en premièr lieu, l'IA récupère toutes les positions du marbles qui se situent sur le plateau du jeu et les mettent dans la liste 'posMarbles'. 

Ensuite, pour chaqu'une marble, si dans les cases d'autours il y a une case vide, il enregistera la position de cette marble dans la liste 'moveOne' de la méthode 'moves'

L'IA prend tout les marbles dans la liste 'moveOne' et vérifie s'il est possible de faire avancer plusieurs marbles dans cette même direction

contrairement, si dans les cases voisines, il y a une direction dont il peut pousser contre une marble adverse, l'IA mettera ces marbles dans la liste 'moveTrain'

pour finir l'IA rassemblera la liste 'moveTrain' et 'moveOne' ensuite il va mélanger l'ordre des élémets de la liste par la méthode random (pour pas avoir à chaque fois les même coups à jouer) 
et il va ranger la liste mélangé en fonction du nombre de marbles à modifier (il va favoriser la modification de 3 marbles en premièr et ensuite la modification de 2 marbles pour favoriver l'attaque)

# méthode negamaxWithPruningIterativeDeepening

cette méthode va appliquer tout les movements possibles l'une à la suite de l'autre qui ont été renvoyé précédement et calculera la différence de marbles entre lui et son adversaire pour chaque possibilité de mouvement,
la méthode negamaxWithPruningIterativeDeepening va ranger l'état du jeu dans 'cache' en fonction de la couleur donné et il reverra le movement le plus favorable à cette couleur au Server.
Le temp de calcul est de 2.8 secondes (car le server exige un temp de réaction de 3 secondes), en fonction de ce temp, il décidera la profondeur du clacul.

l'heuristic de la partie renvoie '9' si le gagnant est lui-même, il renverra '-9' si le gagnant est sont adversaire. Quand il n'y a pas de gangnat, il renvoie la différence de nombre des marbles sur le plateau du jeu
(entre -6 et 6), la manière de calcul est plus offensif que défenssif. S'il doit faire bouger plusieurs marbles, la direction du mouvement sera toujours aligné avec les marbles, les autres directions ne seront pas prises
en compte car cela ne permet pas une attaque directe qui élimine les marbles (la méthode moves renvoie moins de movements possible et donc la méthode negamaxWithPruningIterativeDeepening peu calculer plus en profondeur).
