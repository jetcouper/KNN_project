import numpy as np
#import matplotlib.pyplot as plt
from math import pi
import math
from typing import Tuple, Optional

class KNNNumpy():
    def __init__(self, k , dist, all_images, image_actuel):
        self.__k = k
        self.__dist_max = dist

        self.__all_data, self.__all_label = map(list, zip(*all_images))

        self.__all_data = np.array(self.__all_data)
        self.__all_label = np.array(self.__all_label)

        
        #self.vecteur_3d_image_simple = np.array([self.axe1, self.axe2, self.axe3])


    def predict_image_actuelle(self, image_vector):
        #Prédit la classe de l'image actuelle en utilisant les 3 axes calculés
        return self.predict(image_vector)

    
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
            return None, distance_min, 0
        

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

    # def calculer_vecteur_3d(image):
    #     # Axe 1
    #     axe1 = Axe1.calcul_indice_complexite(image, 0)

    #     # Axe 2
    #     centroid, farthest, percentage = Axe2.analyze_image(image)
    #     axe2 = percentage

    #     # Axe 3
    #     axe3 = Axe3.count_nb_transitions_along__negative_circle(
    #         image, 
    #         center=(int(centroid[1]), int(centroid[0])),
    #         thickness=3
    #     )

    #     return np.array([axe1, axe2, axe3])





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