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
            # égalité, sur le même rang
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

    