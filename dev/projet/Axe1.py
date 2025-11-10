import numpy as np 
from math import *

class Axe1:

    @staticmethod
    #méthode pour calculer l'indice de complexité (première métrique donnée par l'enseignant)
    def calcul_indice_complexite(image, pt=0):
        c = 1 - (4*pi * Axe1.get_area(image, pt))/(Axe1.get_perimeter(image,pt))**2 
        return round(c, 4) 

    @staticmethod
    #méthode pour calculer l'aire en spécifiant en paramètre quel point constitue l'image (1 ou 0)
    def get_area(image,pt):
       image = np.array(image)
       return np.sum(image == pt)
        
    def get_perimeter(image,pt):
        image = np.array(image)
        # y (haut vers bas), x (gauche à droite)
        # slicing -> start | end (exclu) 
        # start index 0 par défaut
        # last index = -1
       
        #Image à analyser = sans les bordures (y = 0, x = 1) jusqu'à la fin (index:-1)
        image_verif = image[1:-1, 1:-1] 
        
        # Création de masques pour chacun des voisins (va couvrir la région qu'on veut analyser)
        # On considère toute l'image par rapport à l'image à vérifier (sans les bordures)
        # Chaque masque vérifie que dans les cases spécifiées, il existe un voisin vide qui correspond à la bordure, donc les pts ne sont pas pareils (vide vs pt image)

        mask1 = (image[0:-2, 1:-1] != image_verif) & (image_verif == pt) # HAUT (y = tout jusqu'à l'avant dernier / x = dim_x image_verif   
        mask2 = (image[2:, 1:-1] != image_verif) & (image_verif == pt) # BAS (y = en partant de la 3e position / x = dim_x image_verif)
        mask3 = (image[1:-1, :-2] != image_verif) & (image_verif == pt) # GAUCHE (y = dim_y img_verif / x = tout jusqu'à l'avant-dernier)
        mask4 = (image[1:-1, 2:] != image_verif) & (image_verif == pt) # DROITE (y = dim_y img_verif / x = tout jusqu'à l'avant-dernier)
        
        #masque diagonaux ->  
        hypo = np.sqrt(2) # valeur du contour => sqrt(1**2 + 1**2)
        mask5 = (image[0:-2, 0:-2] != image_verif) & (image_verif == pt) #HAUT-GAUCHE
        mask6 = (image[0:-2, 2:] != image_verif) & (image_verif == pt) #HAUT-DROITE
        mask7 = (image[2:, 0:-2] != image_verif) & (image_verif == pt) #BAS-GAUCHE
        mask8 = (image[2:, 2:] != image_verif) & (image_verif == pt) #BAS-DROITE

        # puisque le masque renvoie vrai si existe (1), en faisant la sommation on peut trouver tous les points du contour
        voisins = (np.count_nonzero((mask1)) + np.count_nonzero((mask2)) 
                  + np.count_nonzero((mask3)) + np.count_nonzero((mask4))) 
            
        voisins_diagonaux = (np.count_nonzero((mask5)) + np.count_nonzero((mask6))
                            + np.count_nonzero((mask7)) + np.count_nonzero((mask8)))

        perimeter = float(voisins + hypo * (voisins_diagonaux))
        
        return round(perimeter, 4)
    
   
    
    
