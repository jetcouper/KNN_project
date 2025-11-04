import numpy as np
import matplotlib.pyplot as plt

# Image 5x5 avec un carré lumineux au centre
image = np.zeros((5, 5))
image[2:4, 2:4] = 1  # pixels (2,2), (2,3), (3,2), (3,3)

# Coordonnées
r, c = np.meshgrid(np.arange(image.shape[0]), np.arange(image.shape[1]), indexing='ij')

# Calcul du centroïde
area = np.sum(image)
y_centroid = np.sum(r * image) / area
x_centroid = np.sum(c * image) / area

print(f"Centroïde : (y={y_centroid:.2f}, x={x_centroid:.2f})")

# Visualisation
plt.imshow(image, cmap='gray', origin='upper')
plt.scatter(x_centroid, y_centroid, color='red', marker='x', s=100)
plt.title("Centroïde (croix rouge)")
plt.show()
