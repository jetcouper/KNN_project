import numpy as np
import matplotlib.pyplot as plt


class Axe2:
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

        max_index = np.argmax(distances)
        return (y_indices[max_index],x_indices[max_index]), distances[max_index]

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
        return C, farthest, percentage_filled,distance


    # #ces 2 methode permet de visualiser les resultats
    # @staticmethod
    # def draw_circle(image, center, radius=80, thickness=1, value=0):
    #     y, x = center
    #     c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    #     dist2 = (r - y)**2 + (c - x)**2
    #     # Bordure: entre (radius - thickness) et radius
    #     inner_r = max(radius - thickness, 0)
    #     mask = (dist2 >= inner_r**2) & (dist2 <= radius**2)
    #     image[mask] = value  # 0 = noir si image binaire (sinon adapter value)
    #     return image

    # @staticmethod
    # def show(img, data):
    #     Axe2.draw_circle(img, data[0], data[3])
    #     plt.imshow(img, cmap='gray')
    #     plt.scatter([data[0][1]], [data[0][0]], color='red', marker='x', s=100, label='Centroid')
    #     plt.scatter([data[1][1]], [data[1][0]], color='blue', marker='o', s=100, label='Farthest Point')
    #     plt.title(f"Valeur mesurée : {data[2]:.2f}", fontsize=12, color='black', pad=10)
        
    #     plt.axis('off')  # Optionnel : masque les axes
    #     plt.show()



