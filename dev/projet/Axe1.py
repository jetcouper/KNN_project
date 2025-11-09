import numpy as np 
from math import pi

class Axe1:

    @staticmethod
    #méthode pour calculer l'indice de complexité (première métrique donnée par l'enseignant)
    def calcul_indice_complexite(image, pt):
        c = 1 - (4*pi * Axe1.get_area(image, pt))/(Axe1.get_perimeter(image,pt))**2 
        return round(c, 4) 

    @staticmethod
    #méthode pour calculer l'aire en spécifiant en paramètre quel point constitue l'image (1 ou 0)
    def get_area(image,pt):
       image = np.array(image)
       return np.sum(image == pt)
        

    @staticmethod
    #méthode pour calculer le périmètre // méthode à 4 voisins
    def get_perimeter(image,pt):
        image = np.array(image)
        dimy, dimx = image.shape
        outside = int(not pt)
        perimeter = 0

        for i in range(0, dimy-1):
            for j in range(0, dimx-1):

                if image[i,j] == pt:
                    # vérifier s'il y a des cases voisines
                    if image[i-1,j] == outside: #voisin haut
                        perimeter += 1
                    if image[i, j-1] == 0: #voisin gauche
                        perimeter += 1
                    if image[i, j+1] == outside: #voisin droite
                        perimeter += 1
                    if image[i+1, j] == outside: #voisin bas 
                        perimeter += 1 
        
        return perimeter
    
    @staticmethod
    def get_perimeter_by_transitions(image,pt):
        image = np.array(image)
        transitions_y = np.count_nonzero(np.diff(image))
        transitions_x = np.count_nonzero(np.diff(image.T)) 
        transitions = transitions_y + transitions_x
        return transitions
    
    def get_perimeter_mixte(image,pt):
        image = np.array(image)
        # y (haut ver bas), x (gauche à droite)
        #all voisins
        # en numpy, la position de départ est zéro 
        # en slicing, stop est une borne exclusive, donc on ne va pas inclure l'élément 
       
        #image sans border : on retire la bordure du haut et la dernière colonne, 
        # donc on part à 1 vs 0 et on bloque les bornes avec -1
        image_verif = image[1:-1, 1:-1] # y, x
        
        mask1 = (image[0:-2, 1:-1] != image_verif) & (image_verif == pt) #HAUT y-1, x
        mask2 = (image[2:, 1:-1] != image_verif) & (image_verif == pt) #BAS y+1, x
        mask3 = (image[1:-1, :-2] != image_verif) & (image_verif == pt) #GAUCHE
        mask4 = (image[1:-1, 2:] != image_verif) & (image_verif == pt) #DROITE
        # image_verif[mask1] = 3
        # image_verif[mask2] = 2
        # image_verif[mask3] = 5
        # image_verif[mask4] = 4
        #print(image_verif[mask1])
        
        perimeter = np.count_nonzero((mask1)) + np.count_nonzero((mask2)) + np.count_nonzero((mask3)) + np.count_nonzero((mask4))

        return perimeter
    
image_test = [      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
                    [0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
                    [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
                    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
                    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
                    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
                    [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
                    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
                    [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ]

image_test2 = [     [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,1,1,1,1,0,0],
                    [0,0,1,1,1,1,0,0],
                    [0,0,1,1,1,1,0,0],
                    [0,0,1,1,1,1,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0]]

image_star = [ # aire à 121 // perimetre à 48 s
 [0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0],
 [0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
 [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
 [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
 [0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
 [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
 [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
 [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
 [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
 [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
 [0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
 [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
 [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
 [0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0]
]

    # --- exécution du test
if __name__ == "__main__":

    #print(Axe1.get_area(image_star,1))
    print(Axe1.get_perimeter(image_star, 1))
    print(Axe1.get_perimeter_by_transitions(image_star,1))
    #print(Axe1.calcul_indice_complexite(image_star,1))
    print(f'perimetre : {Axe1.get_perimeter_mixte(image_star,1)}')
