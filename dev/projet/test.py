import numpy as np
from math import *

def get_perimeter(image):
    
    image = np.array(image)
    dimy, dimx = image.shape #pour obtenir la taille pour chacune des dimensions selon les axes y et x
    perimeter = 0
    #masque = np.zeros((dimy, dimx), dtype=int) #crée une matrice temporaire de même taille que l'image remplie de 0 
    
    perimeter = np.count_nonzero(np.diff(image)) + np.count_nonzero(np.diff(image.T))

    #transitions_y = np.append(transitions_y, np.where(np.count_nonzero(np.diff(image))))

    transitions = np.where(np.diff(image))
    transitions = np.append(transitions, np.where(np.diff(image.T)))
    #print(transitions)
    #transitions_y = np.where(np.diff(image))
    #transitions_x = np.where(np.diff(image.T))
    # perimetre diagonal
    hypo = ((1)**2 + (1)**2)**0.5

    # for y in range(transitions.size):
    #     print(y)
    #     i, j = (transitions[0][y+2], transitions[1][y+2])
    #     print(pt_ici)

    #     all_voisins = [image[i - 1, j - 1], image[i - 1, j], image [i - 1, j + 1], #8 voisins à vérifier 
    #                             image[i, j - 1],                      image[i, j + 1],
    #                             image [i + 1, j - 1], image[i + 1, j], image[i + 1, j + 1]  
    #                         ]
        
    #     if sum(all_voisins) == 3:
    #         perimeter += hypo
    #     else:
    #         perimeter += 1
   
    
    #     if y+2 >= transitions[0].size: break
    #     pt_suivant = (transitions[0][y+2], transitions[1][y+2])
    #     if (abs(pt_suivant[0] - pt_ici[0]) and abs(pt_suivant[1] - pt_ici[1])):
    #         image[transitions[1][y]][transitions[0][y]] = 4
    # nb_diagonales = np.count_nonzero(image[image == 4])
    # print(nb_diagonales)
    # for i in range(nb_diagonales):
    #     perimeter += 0.414
    
    return perimeter

def calcul_indice_complexite(image, pt):
    area = get_area(image,pt)
    perimeter = get_perimeter(image)
    c = 1 - ((4*pi * area)/(perimeter**2))
    return round(c,4) 


def get_area(image, pt):
    
    area = 0
    liste = np.array(image)
    dimx = liste.shape[0]
    dimy = liste.shape[1]

    for x in np.arange(dimx):
        for y in np.arange(dimy):
            if liste[x,y] == pt:
                area += 1
    
    return area

def get_area_too(image):
    return np.sum(image)




# on fait la distance euclidienne


image_test = [  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
                [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
                [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
                [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
                [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
                [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
                [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
                [0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ]


image_test2 = [ [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,1,1,1,1,0,0],
                [0,0,1,1,1,1,0,0],
                [0,0,1,1,1,1,0,0],
                [0,0,1,1,1,1,0,0],
                [0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0]]

# print(f'aire grand cercle : {get_area(image_test, 1)}')
# print(f' aire externe du cercle : {get_area(image_test, 0)}')
print(f' perimetre grand cercle : {get_perimeter(image_test)}')
print(f'index de complexité : {calcul_indice_complexite(image_test, 1)}')

# print(f'aire du petit carré {get_area(image_test2, 1)}')
# print(f'aire externe carré: {get_area(image_test2, 0)}')
# print(f'perimetre carré {get_perimeter(image_test2)}')

