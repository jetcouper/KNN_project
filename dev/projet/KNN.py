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
    
    def get_perimeter(self, image, x, y):
    
        perimeter = 0
        rows = image.shape[0]
        cols = image.shape[1]
        
        #toutes les directions à vérifier 
        directions = np.array([(-1, -1), (0, -1), (1, -1),
                                (-1, 0),           (0, 1),
                                (-1, 1),   (1,1),  (1, 1),
                            ])
        
        coordx = directions[0]
        coordy = directions[1]
        
        for (x in range rows):
            
            for(y in range cols):
                
                if(image[x,y] == 0):
                    
                    for(coordx, coordy in directions):
                        
                        if(image[x + coordx, y + coordy] == 0):
                            perimeter += 1
                        
    
     return perimeter
            
        
    def get_area(self, img): 
        a = np.sum(img[img != 0]) #images sont noirs -> 0
        return a 
        
    def matrice1(self, aire):
        
        c = 1 - (4 * np.pi * aire) / np.pi ** 2
        return c
    
    
    def matrice2(self, img):
        
        d = 0 #densité (d = a/b)
        a = 0 #aire de la forme
        b = 0 #aire du cercle
        r = 0 #rayon du plus grand segment entre centroide et tous les pts du perimetres
        
        
    # size = (150,150)
    
    # image = np.full((size[0], size[1]), 0)
    
    # get_perimeter(image)