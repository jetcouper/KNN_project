import numpy as np

from db_credential import PostgreSQLCredential
from klustr_dao import PostgreSQLKlustRDAO

class test1:
    def __init__(self, image, klustrDao):
        self.image = image
        self.k = 0  # Number of neighbors
        self.X_train = None
        self.y_train = None
        self.z_train = None
        
        #credential = PostgreSQLCredential(password='AAAaaa123')
        dao = klustrDao
        
        #self.liste_matrices = dao.all_images_to_np(10)
        #print(f'taille de la liste de matrices : {len(self.liste_matrices)}')
        #
        #if self.liste_matrices:
        #    print("Forme de la première image :", self.liste_matrices[0].shape)
        #   
        #else:
        #    print("Aucune image")

    def fit(self, X, Y, Z):
        self.X_train = X
        self.y_train = Y
        self.z_train = Z

    
    def get_perimeter(image):
        
        image = np.array(image)
        dimy, dimx = image.shape #pour obtenir la taille pour chacune des dimensions selon les axes y et x
        print(f'{dimx}')
        perimeter = 0
        # liste = np.array(image)
        # dimx = liste.shape[0]
        # dimy = liste.shape[1]
        masque = np.zeros((dimy, dimx), dtype=int) #crée une matrice temporaire de même taille que l'image remplie de 0 
        
        # ici on retire chaque dernier point des extrémités => (i - 1), (i + 1)
        for i in range(0, dimy - 1):
            for j in range(0, dimx - 1):
            
                 #toutes les voisins à vérifier sauf les extrémités 
                all_voisins = [image[i - 1, j - 1], image[i - 1, j], image [i - 1, j + 1], #8 voisins à vérifier 
                                image[i, j - 1],                      image[i, j + 1],
                                image [i + 1, j - 1], image[i + 1, j], image[i + 1, j + 1]  
                            ]
                
                # pour les voisins en diagonal, distance euclidienne 
                hypo = ((1)**2 + (1)**2)**0.5
                #hypo = 1.41421356

                if image[i, j] == 1: #pour chaque pixel

                    # if image[i - 1, j - 1] == 0: #haut gauche
                    #     perimeter += hypo #racine 2
                    
                    if image[i - 1, j] == 0: #haut
                        perimeter += 1
                    
                    # if image[i - 1, j + 1] == 0: #haut droite
                    #     perimeter += hypo #racine 2

                    if image[i, j - 1] == 0: #gauche
                        perimeter += 1
                    
                    if image[i, j + 1] == 0: #droite
                        perimeter += 1
    
                    # if image[i + 1, j - 1] == 0: #bas gauche
                    #     perimeter += hypo #racine 2

                    if image[i + 1, j] == 0: #bas 
                        perimeter += 1 
                        
                    # if image[i + 1, j + 1] == 0: #bas droite
                    #     perimeter += hypo #racine 2

                # verif_nbvoisins = sum(all_voisins)
            
                # if (verif_nbvoisins <= 7 and image[i, j] == 1): #si on a moins 1 voisin et qu'on est un pixel de l'image
                #  masque[i, j] = 1 #on indique dans la matrice masque l'emplacement où se trouve les extrémités contours

        # for x in np.arange(dimx):
        #     for y in np.arange(dimy):
        #             if liste[x,y] == 1:
        #                 for x in coordx:
        #                     for y in coordy:
        #                         if(np.any(liste[x + coordx, y + coordy]) == 0): #inclut 0 et extérieur
        #                             pt = (x + coordx, y + coordy)
        #                             if pt in liste_contour:
        #                                 liste_contour.append(pt)
        
        # perimeter = len(liste_contour) # * ((1**2) + (1**2))**0.5 # on fait la distance euclidienne
        
        #perimeter = np.sum(masque) #on retient tout ce qui équivaut à 1, donc le contour de l'image
        
        return round(perimeter,2)

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


    print(f'aire grand cercle : {get_area(image_test, 1)}')
    print(f' aire externe du cercle : {get_area(image_test, 0)}')
    print(f' perimetre grand cercle : {get_perimeter(image_test)}')


    print(f'aire du petit carré {get_area(image_test2, 1)}')
    print(f'aire externe carré: {get_area(image_test2, 0)}')
    print(f'perimetre carré {get_perimeter(image_test2)}')

    # --- exécution du test
if __name__ == "__main__":
    
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
    
    #test1(image_test)