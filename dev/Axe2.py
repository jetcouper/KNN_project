import numpy as np

import matplotlib.pyplot as plt


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
        distances = np.linalg.norm(np.array([x_indices - centroid[1], y_indices - centroid[0]]), axis=0)
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
        
        return (filled_area / total_area) * 100

    @staticmethod
    def analyze_image(image):
        C = Axe2.centroid(image)
        farthest, distance = Axe2.farthest_point(image, C)
        percentage_filled = Axe2.filled_percentage(image, C, distance)
        return C, farthest, percentage_filled

    @staticmethod
    def show(img, centroid, farthest_point):
        plt.imshow(img, cmap='gray')
        plt.scatter([centroid[0][1]], [centroid[0][0]], color='red', marker='x', s=100, label='Centroid')
        plt.scatter([farthest_point[1][0]], [farthest_point[1][1]], color='blue', marker='o', s=100, label='Farthest Point')
        plt.axis('off')  # Optionnel : masque les axes
        plt.show()

# size = 100
# circle_image = np.zeros((size, size), dtype=int)

# radius = 30
# center = (size // 2, size // 2)  # milieu de l'image
# Axe2.draw_circle(circle_image, center, radius)


# result = Axe2.analyze_image(circle_image)
# print("Centroïde:", result[0])
# print("Point le plus éloigné:", result[1][0], result[1][1])
# print("Pourcentage d'espace rempli dans le cercle:", result[2])



