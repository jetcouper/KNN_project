import math
import numpy as np
from typing import Tuple

class Axe3:
    @staticmethod
    def count_nb_transitions_along__negative_circle(
        grid: np.ndarray, 
        center: Tuple[int, int] = None, 
        radius: float = None, 
        thickness: int = 1,
        radius_ratio: float = 0.6  # NOUVEAU : paramètre ajustable
    ) -> float:
        """
        Compte le nombre de transitions noir-blanc sur le tour d'un cercle.
        
        :param grid: np.ndarray 2d binaire (0=forme, 1=fond)
        :param center: Coordonnées (x, y) du centre du cercle
        :param radius: Rayon du cercle (si None, calculé automatiquement)
        :param thickness: Épaisseur du cercle pour moyenner les valeurs
        :param radius_ratio: Ratio pour le calcul auto du rayon (0.5-0.8 recommandé)
        :return: Nombre de transitions normalisé
        """
        rows, cols = grid.shape
        
        if center is None:
            center = (cols // 2, rows // 2)
        
        if radius is None:
            # Essayer différentes valeurs : 0.5, 0.6, 0.7, 0.8
            radius = min(rows, cols) // 2 * radius_ratio
        
        cx, cy = center
        
        # Diviser le cercle en samples
        num_samples = 360
        samples = []
        
        for i in range(num_samples):
            angle = 2 * math.pi * i / num_samples
            
            total_value = 0
            valid_samples = 0
            
            for t in range(-thickness // 2, thickness // 2 + 1):
                r = radius + t
                x = int(cx + r * math.cos(angle))
                y = int(cy + r * math.sin(angle))
                
                if 0 <= y < rows and 0 <= x < cols:
                    # Inverser : forme (0) devient 1
                    total_value += (1 - grid[y, x])
                    valid_samples += 1
            
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
        
        normalized_transitions = transitions / num_samples
        
        return normalized_transitions
    