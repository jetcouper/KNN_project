

import numpy as np
from PySide6 import QtGui, QtCore



# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QImage

# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------


class QtNpConvert:

    @staticmethod
    def qimage_from_png(img_data: bytes, verbose_instead_of_raise: bool = True) -> QImage:
        '''Effectue le décodage d'un 'buffer' de données correspondant à une 
        image PNG. 

        En entrée se trouve le 'buffer' conforme d'une image de format PNG.

        En sortie on obtient une QImage du format QImage.Format_ARGB32.'''
        image = QImage()
        if image.load_from_data(QByteArray(bytearray(img_data)), 'png'):
            return image.convert_to_format(QImage.Format_ARGB32)

        message = "Erreur de décodage d'une image avec la fonction 'QtNpConvert.qimage_from_png'."
        if verbose_instead_of_raise:
            print(message)
            return image
        else:
            raise ValueError(message)
        
    @staticmethod
    def np_from_qimage(img : QImage, verbose: bool = True) -> np.ndarray:
        '''Effectue la conversion d'une image de format 
        QImage.Format_ARGB32 vers une matrice numpy.

        L'image d'entrée doit respectée le format spécifié et correspondre 
        à une image binaire avec les couleurs noir et blanc.

        L'image de sortie est convertie en une matrice de la même taille ayant des valeurs 0-1 en format uint8.'''
        if not isinstance(img, QImage):
            raise TypeError("Erreur dans la fonction 'QtNpConvert.np_from_qimage' : img doit être un QImage")
        if img.format() != QImage.Format_ARGB32:
            img = img.convert_to_format(QImage.Format_ARGB32)
            if verbose:
                print('Attention, il est attendu que img soit de format ARGB32. Une conversion a été effectuée.')
        return (np.frombuffer(img.bits(), dtype=np.uint32).reshape((img.height(), img.width())) != 0xFF000000).astype(np.uint8)        


    @staticmethod
    def qimage_argb32_from_png_decoding(img_data):
        '''Effectue le décodage d'un 'buffer' de données correspondant à une 
        image PNG. 

        En entrée se trouve le 'buffer' conforme d'une image de format PNG.

        En sortie on obtient une QImage du format QImage.Format_ARGB32.'''
        image = QtGui.QImage()
        if image.load_from_data(QtCore.QByteArray(bytearray(img_data)), 'png'):
            return image.convert_to_format(QtGui.QImage.Format_ARGB32)
        
        print("Erreur de décodage d'une image avec la fonction 'qimage_argb32_from_png_decoding'.")
        return image

    @staticmethod
    def ndarray_from_qimage_argb32(img : QtGui.QImage) -> np.ndarray:
        '''Effectue la conversion d'une image de format 
        QImage.Format_ARGB32 vers une matrice numpy.

        L'image d'entrée doit respectée le format spécifié et correspondre 
        à une image binaire avec les couleurs noir et blanc.

        L'image de sortie est convertie en une matrice de la même taille ayant des valeurs 0-1 en format uint8.'''
        if not isinstance(img, QtGui.QImage):
            raise TypeError("Erreur dans la fonction 'ndarray_from_qimage_argb32' : img doit être un QImage")
        if img.format() != QtGui.QImage.Format_ARGB32:
            img = img.convert_to_format(QtGui.QImage.Format_ARGB32)
            print('Attention, il est attendu que img soit de format ARGB32. Une conversion a été effectuée.')
        return (np.frombuffer(img.bits(), dtype=np.uint32).reshape((img.height(), img.width())) != 0xFF000000).astype(np.uint8)
    
    @staticmethod #méthode par Antoine 
    def qimage_to_numpy(qimage):
        """Convertit une QImage en numpy array"""

        width = qimage.width()
        height = qimage.height()

        # Convertir en format RGB32 si nécessaire
        if qimage.format() != QImage.Format_RGB32:
            qimage = qimage.converted_to(QImage.Format_RGB32)

        # Obtenir les données brutes
        ptr = qimage.bits()

        # Créer le numpy array
        # Format RGB32 : 4 bytes par pixel (R, G, B, A)
        arr = np.array(ptr).reshape(height, width, 4)

        # Garder seulement RGB (sans alpha)
        arr = arr[:, :, :3]

        return arr