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

    #def matrice1(self):
        #c = 1 - (4 * pi *aire) / pi^2
