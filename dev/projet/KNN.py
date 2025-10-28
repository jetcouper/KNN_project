import numpy as np

class KNN:
    def __init__(self, image):
        self.image = image
        self.k = 0  # Number of neighbors
        self.X_train = None
        self.y_train = None
        self.z_train = None

    def fit(self, X, Y, Z):
        self.X_train = X
        self.y_train = Y
        self.z_train = Z

    def get_perimeter(image):
        
            perimeter = 0
            liste_contour = []
            liste = np.array(image)
            dimx = liste.shape[0]
            dimy = liste.shape[1]

            #toutes les directions à vérifier 
            directions = np.array([(-1, -1), (0, -1), (1, -1), #8 voisins à vérifier 
                                    (-1, 0),           (0, 1),
                                    (-1, 1),   (1,1),  (1, 1),
                                ])
            
            coordx = directions[0]
            coordy = directions[1]

            for x in np.arange(dimx):
                for y in np.arange(dimy):
                        if liste[x,y] == 1:
                            for x in coordx:
                                for y in coordy:
                                    if(np.any(liste[x + coordx, y + coordy]) == 0): #inclut 0 et extérieur
                                        pt = (x + coordx, y + coordy)
                                        if pt in liste_contour:
                                         liste_contour.append(pt)
            
            perimeter = len(liste_contour) # * ((1**2) + (1**2))**0.5 # on fait la distance euclidienne

            return perimeter 

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

    print(get_area(image_test, 1))
    print(get_area(image_test, 0))
    print(get_perimeter(image_test))


    print(get_area(image_test2, 1))
    print(get_area(image_test2, 0))
    print(get_perimeter(image_test2))

    