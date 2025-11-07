import numpy as np
#import matplotlib.pyplot as plt
from math import pi
import math
from typing import Tuple, Optional
# # poids - sucre - eau
# data = [

#     # Pommes
#     [
#         [180, 10, 84],
#         [170, 11, 85],
#         [160, 9, 83],
#         [175, 10.5, 84],
#         [165, 9.5, 85],
#     ],
#     # Bananes
#     [
#         [120, 20, 74],
#         [130, 21, 73],
#         [125, 19.5, 75],
#         [135, 22, 72],
#         [128, 20.5, 74],
#     ],
#     # Pommes de terre
#     [
#         [200, 1, 79],
#         [210, 0.8, 78],
#         [190, 1.2, 80],
#         [205, 1, 79],
#         [195, 0.9, 81]
#     ]
# ]

# label = [
    
#     # Pommes
#     ["pomme", "pomme", "pomme", "pomme", "pomme"],

#     # Bananes
#     ["banane", "banane", "banane", "banane", "banane"],

#     # Pommes de terre
#     ["patate", "patate", "patate", "patate", "patate"]
# ]

class KNNNumpy():
    def __init__(self, k , dist, all_images, image_actuel):
        self.__k = k
        self.__dist_max = dist

        self.__all_data, self.__all_label = map(list, zip(*all_images))
        
        self.__image_actuel = image_actuel

        self.axe1 = Axe1.calcul_indice_complexite(self.__image_actuel,0)
        centroid, farthest, percentage = Axe2.analyze_image(self.__image_actuel)
        self.axe2 = percentage

        self.axe3 = Axe3.count_nb_transitions_along__negative_circle(
            self.__image_actuel, 
            center=(int(centroid[1]), int(centroid[0])),  # Le centroid calculé
            thickness=3
        )
        self.vecteur_3d_image_simple = np.array([self.axe1, self.axe2, self.axe3])


    def predict_image_actuelle(self):
        #Prédit la classe de l'image actuelle en utilisant les 3 axes calculés
        return self.predict(self.vecteur_3d_image_simple)

    
    def add_point(self, data, label):
        """
        ========= exemple d'utilisation =========
        knn_n.add_point([150, 0.3, 72], "pomme")
        """
        if len(self.__all_data) == 0:
            self.__all_data = np.array([data])
            self.__all_label = np.array([label])
        else:
            self.__all_data = np.append(self.__all_data, [data], axis=0)
            self.__all_label = np.append(self.__all_label, label)
        
    def add_points(self, all_data, all_label): 
            """
            ========= exemple d'utilisation =========
            knn_n.add_points(np.array([[150, 0.3, 72], [200, 0.8, 50]]), np.array(["pomme", "banane"]))
            """
            self.__all_data = np.array(all_data)
            self.__all_label = np.array(all_label)

    @property
    def all_data(self):
        return self.__all_data
    @property
    def dist_max(self):
        return self.__dist_max
    @property
    def all_label(self):
        return self.__all_label
            
    def predict(self, image):
        
        image = np.array(image)

        # calculer la distance ( la norme )
        distances_array = np.linalg.norm(self.__all_data - image, axis=1)
        
        # ensuite il faut les trier
        k_indices = np.argsort(distances_array)[:self.__k]
        k_distances = distances_array[k_indices]
        k_labels = self.all_label[k_indices]


        distance_min = k_distances[0]
        if distance_min > self.__dist_max:
            return None, distance_min, 0,0
        

        # compter celui qui a le plus de fois le meme type
        unique, compte = np.unique(k_labels, return_counts=True)

        max_count = np.max(compte)
        tied_labels = unique[compte == max_count]


        if len(tied_labels) > 1:
            # Cas d'ex-aequo : calculer la distance moyenne pour chaque classe ex-aequo
            best_label = None
            best_avg_distance = float('inf')
            
            for label in tied_labels:
                label_distances = k_distances[k_labels == label]
                avg_distance = np.mean(label_distances)
                
                if avg_distance < best_avg_distance:
                    best_avg_distance = avg_distance
                    best_label = label
            
            predicted_label = best_label
            avg_distance = best_avg_distance
        else:
            # Cas normal : une seule classe majoritaire
            predicted_label = unique[np.argmax(compte)]
            avg_distance = np.mean(k_distances[k_labels == predicted_label])
        
        # Calculer un indice de confiance (0 à 1)
        # Plus la distance est petite par rapport à dist_max, plus la confiance est élevée
        confiance = max(0, 1 - (avg_distance / self.__dist_max))





        return predicted_label, avg_distance, confiance

    @property
    def k(self):
        return self.__k
    
    @k.setter
    def k(self, k):
        if not(1 <= k <= len(self.__all_label)):
            raise ValueError("k doit être entre 1 et " + str(len(self.__all_label)))
        self.__k = k

    @property
    def ndim(self):
        if len(self.__all_data == 0):
            return 0
        return len(self.__all_data[0])

    def calculer_vecteur_3d(image):
        # Axe 1
        axe1 = Axe1.calcul_indice_complexite(image, 0)

        # Axe 2
        centroid, farthest, percentage = Axe2.analyze_image(image)
        axe2 = percentage

        # Axe 3
        axe3 = Axe3.count_nb_transitions_along__negative_circle(
            image, 
            center=(int(centroid[1]), int(centroid[0])),
            thickness=3
        )

        return np.array([axe1, axe2, axe3])


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

class Axe2:
    @staticmethod
    # Fonction pour dessiner un cercle dans l'image
    def draw_circle(image, center, radius=30):
        x, y = center
        c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        image[((r - y)**2 + (c - x)**2) <= radius**2] = 1

    @staticmethod
    # Fonctions de calculs
    def area(image):
        return np.sum(image)

    @staticmethod
    def centroid(image):
        c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        return (np.sum(r * image), np.sum(c * image)) / Axe2.area(image)

    @staticmethod
    def farthest_point(image, centroid):
        y_indices, x_indices = np.nonzero(image)
        distances = np.sqrt((x_indices - centroid[1])**2 + (y_indices - centroid[0])**2)

        #distances = np.linalg.norm(np.array([x_indices - centroid[1], y_indices - centroid[0]]), axis=0)
        max_index = np.argmax(distances)
        return (x_indices[max_index], y_indices[max_index]), distances[max_index]

    @staticmethod
    def filled_percentage(image, center, radius):
        y, x = np.ogrid[-center[1]:image.shape[0]-center[1], -center[0]:image.shape[1]-center[0]]
        mask = x**2 + y**2 <= radius**2

        filled_area = np.sum(image[mask])
        total_area = np.sum(mask)

        if total_area == 0:
            return 0.0
        
        return (filled_area / total_area)

    @staticmethod
    def analyze_image(image):
        C = Axe2.centroid(image)
        farthest, distance = Axe2.farthest_point(image, C)
        percentage_filled = Axe2.filled_percentage(image, C, distance)
        return C, farthest, percentage_filled

    @staticmethod
    def show(img, centroid, farthest_point):
        # plt.imshow(img, cmap='gray')
        # plt.scatter([centroid[0][1]], [centroid[0][0]], color='red', marker='x', s=100, label='Centroid')
        # plt.scatter([farthest_point[1][0]], [farthest_point[1][1]], color='blue', marker='o', s=100, label='Farthest Point')
        # plt.axis('off')  # Optionnel : masque les axes
        # plt.show()
        pass



class Axe3:
    @staticmethod
    def count_nb_transitions_along__negative_circle(grid: np.ndarray, center: Tuple[int, int] = None, radius: float = None, thickness: int = 1) -> int:
        """
        Counts the number of points on a star by analyzing black-to-white transitions
        along a circular path.
        
        :param grid: 2D numpy array representing the star (1 = black/star, 0 = white/background)
        :param center: (x, y) coordinates of circle center. If None, uses grid center
        :param radius: Radius of the sampling circle. If None, uses 70% of half the grid size
        :param thickness: Thickness of the sampling circle (how many pixels to average)
        :return: Number of points detected (transitions / 2)
        """
        """
        Compte le nombre de transitions noir-blanc sur le tour d'un cercle imaginare superposé sur le centroid d'une forme donnée.
        :param grid: np.ndarray 2d binaire représentant une forme.
        :param center: Coordonnées (x, y) du centre du cercle imaginaire. Si non spécifié, il utilise le centre de la grille.
        :param radius: Rayon du cercle imaginaire. Si non spécifié, il utilise 70 % de la moitié de la taille de la grille.
        :param thickness: Épaisseur du cercle imaginaire. Chaque échantillons pris sur les 360 degrés du cercle représente la moyenne de cette épaisseur du cercle afin d'éviter des erreurs du à la faible qualité des images.
        :return: Nombre de transitions détectés.
        """
        rows, cols = grid.shape
        
        if center is None:
            center = (cols // 2, rows // 2)
        
        if radius is None:
            radius = min(rows, cols) // 2 * 0.7
        
        cx, cy = center
        
        # Diviser le cercle en samples pour trouver les transitions
        num_samples = 360
        samples = []
        
        for i in range(num_samples):
            angle = 2 * math.pi * i / num_samples
            
            # Faire la moyenne de l'épaisseur des samples
            total_value = 0
            valid_samples = 0
            
            for t in range(-thickness // 2, thickness // 2 + 1):
                r = radius + t
                x = int(cx + r * math.cos(angle))
                y = int(cy + r * math.sin(angle))
                
                if 0 <= y < rows and 0 <= x < cols:
                    total_value += grid[y, x]
                    valid_samples += 1
            
            # Attribuer une valeure binaire à chaque sample selon leur moyenne
            if valid_samples > 0:
                avg_value = total_value / valid_samples
                samples.append(1 if avg_value >= 0.5 else 0)
            else:
                samples.append(0)
        
        # Compter les transitions
        transitions = 0
        for i in range(len(samples)):
            current = samples[i]
            next_sample = samples[(i + 1) % len(samples)]
            
            if abs(current - next_sample) == 1:
                transitions += 1
        
        return transitions

    

#if "__main__" == __name__:
#    
#    knn_n = KNNNumpy()
#
#    image = [150, 0.3, 72]
#
#    # knn_n.add_point([1501, 0.3, 72], "pomme")
#    # knn_n.add_point([1502, 0.3, 72], "patate")
#    # knn_n.add_point([1503, 0.3, 72], "banane")
#    # knn_n.add_point([1504, 0.3, 72], "pomme")
#    # knn_n.add_point([1504, 0.3, 72], "pomme")
#    # knn_n.add_point([1504, 0.3, 72], "pomme")
#    knn_n.add_points(np.array([[150, 0.3, 72], [150, 0.3, 72], [200, 0.8, 50]]), np.array(["pomme", "pomme", "banane"]))
#
#    knn_n.k = 2
#    resultat = knn_n.predict(image)
#
#    print(knn_n.all_label)
#    print(knn_n.all_data)
#    
#    print("Résultat :", resultat)
#    print("Dimensions :", knn_n.ndim)