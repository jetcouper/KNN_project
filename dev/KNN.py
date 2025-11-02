import numpy as np
# poids - sucre - eau
data = [

    # Pommes
    [
        [180, 10, 84],
        [170, 11, 85],
        [160, 9, 83],
        [175, 10.5, 84],
        [165, 9.5, 85],
    ],
    # Bananes
    [
        [120, 20, 74],
        [130, 21, 73],
        [125, 19.5, 75],
        [135, 22, 72],
        [128, 20.5, 74],
    ],
    # Pommes de terre
    [
        [200, 1, 79],
        [210, 0.8, 78],
        [190, 1.2, 80],
        [205, 1, 79],
        [195, 0.9, 81]
    ]
]

label = [
    
    # Pommes
    ["pomme", "pomme", "pomme", "pomme", "pomme"],

    # Bananes
    ["banane", "banane", "banane", "banane", "banane"],

    # Pommes de terre
    ["patate", "patate", "patate", "patate", "patate"]
]

class KNNNumpy():
    def __init__(self):
        self.__k = 3
        
        self.__all_data = np.array([])
        self.__all_label = np.array([], dtype=object)
    
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
    def all_label(self):
        return self.__all_label
            
    def predict(self, image):
        
        image = np.array(image)

        # calculer la distance ( la norme )
        distances_array = np.linalg.norm(self.__all_data - image, axis=1)
        
        # ensuite il faut les trier
        k_indices = np.argsort(distances_array)[:self.__k]

        k_labels = self.all_label[k_indices]

        # compter celui qui a le plus de fois le meme type
        u, indices = np.unique(k_labels, return_counts=True)

        return u[np.argmax(indices)]

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

if "__main__" == __name__:
    
    knn_n = KNNNumpy()

    image = [150, 0.3, 72]

    # knn_n.add_point([1501, 0.3, 72], "pomme")
    # knn_n.add_point([1502, 0.3, 72], "patate")
    # knn_n.add_point([1503, 0.3, 72], "banane")
    # knn_n.add_point([1504, 0.3, 72], "pomme")
    # knn_n.add_point([1504, 0.3, 72], "pomme")
    # knn_n.add_point([1504, 0.3, 72], "pomme")
    knn_n.add_points(np.array([[150, 0.3, 72], [150, 0.3, 72], [200, 0.8, 50]]), np.array(["pomme", "pomme", "banane"]))

    knn_n.k = 2
    resultat = knn_n.predict(image)

    print(knn_n.all_label)
    print(knn_n.all_data)
    
    print("Résultat :", resultat)
    print("Dimensions :", knn_n.ndim)

