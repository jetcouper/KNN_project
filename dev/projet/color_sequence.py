
from math import floor, log2


# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtGui import QColor

# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------



class QColorSequence:
    """
    Cette classe sert à générer une séquence de couleurs distinctes en 
    utilisant un algorithme basé sur le modèle de couleur HSL (Hue, 
    Saturation, Lightness).

    Le pattern de génération de couleur est conçu pour maximiser la 
    différenciation entre les couleurs consécutives. Pour ce faire, le 
    paramètre 'Hue' (Teinte) est calculé en fonction du nombre de fois où 
    la méthode `next()` a été appelée (`__n`), de manière à espacer 
    uniformément les couleurs sur le cercle chromatique HSL.

    Attributs statiques :
        s (float): La saturation de la couleur dans le modèle HSL, fixée à 1.0 par défaut.
        l (float): La luminosité de la couleur dans le modèle HSL, fixée à 0.5 par défaut.
        
    Méthode statique :
        reset(): Réinitialise la séquence de couleur.
        
    Exemples:
        >>> seq = QColorSequence()
        >>> color1 = seq.next()
        >>> color2 = seq.next()
        >>> color1 != color2
        True
    """

    __n = 0
    s = 1.0
    l = 0.5

    @staticmethod
    def next() -> QColor:
        """
        Retourne la prochaine couleur dans la séquence.

        Retourne:
            QColor: La prochaine couleur dans la séquence de couleur.

        Exemples:
            >>> seq = QColorSequence()
            >>> QColorSequence.s = 0.75
            >>> QColorSequence.l = 0.45
            >>> color = seq.next()
            >>> isinstance(color, QColor)
            True
        """
        QColorSequence.__n += 1
        size = 2 ** floor(log2(QColorSequence.__n))
        index = QColorSequence.__n - size
        h = 1 / size * (index + 0.5)
        return QColor.from_hsl_f(h, QColorSequence.s, QColorSequence.l)
        # return QColor.fromHslF(h, QColorSequence.s, QColorSequence.l)

    @staticmethod
    def reset() -> None:
        """Réinitialise la séquence de couleur."""
        QColorSequence.__n = 0


# print(QColorSequence.next())
