import math
import numpy as np
from typing import Tuple

class Axe3:
    @staticmethod
    def count_nb_transitions_along__negative_circle(grid: np.ndarray, center: Tuple[int, int] = None, radius: float = None, thickness: int = 1) -> float:
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
        
        # Normaliser
        max_transitions = num_samples
        normalized_transitions = transitions / max_transitions
        
        return normalized_transitions