# Informations spécifiques à PySide6

## Utilisation de snake_case et true_property

Qt utilise la convention de nommage `camelCase` pour les méthodes et les propriétés et possède un mécanisme interne de propriété, les deux étant des artefacts du C++. Cependant, Python favorise la convention `snake_case` et recommande l'usage explicite des propriétés. Pour rendre l'API plus _pythonic_, PySide6 offre la possibilité d'utiliser `snake_case` pour les méthodes et `true_property` pour les propriétés. 

_Note_ : il existe quelques exceptions à cette règle mais nous porterons une attention particulière aux signaux qui gardent la convention `camelCase`. Par exemple, `valueChanged`, `mousePressed`, .... Ces signaux gardent la convention `camelCase` et ne deviennent pas `value_changed`, `mouse_pressed`, ....

### Cas simples
Pour les petits projets où on retrouve un seul module Qt, il suffit d'insérer cette ligne de code à la fin de vos importations de PySide6 :
```python
# ... importation des modules PySide6 ...

from __feature__ import snake_case, true_property  
```

Cette ligne génère cependant un avertissement dans les IDE (PyCharm, VSCode, etc.) car l'analyseur statique ne trouve pas le module `__feature__`. C'est normal car ce module n'existe pas physiquement. Il est généré dynamiquement par Shiboken6 (le binding de PySide6).

Pour palier à cet irritant, on peut explicitement spécifier à l'IDE d'ignorer cette erreur d'importation en ajoutant le commentaire suivant à la fin de la ligne. 
```python
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
```

### Importations de sous modules

Pour les projets où on utilise plusieurs modules Qt personnalisés, il existe un problème d'importation où les modules activent et désactivent les caractéristiques `snake_case` et `true_property` des fichiers importés de manière incohérente. Pour résoudre ce problème, il est recommandé d'utiliser le module `shibokensupport` pour activer manuellement ces fonctionnalités. Voici une solution simple à mettre en oeuvre dans **tous** vos fichiers utilisant Qt. Évidemment, d'autres solutions plus élaborées sont possibles.

```python
# Selon la convention PEP 8 importer les modules dans cet ordre :
# 0. précéder vos importations par la docstring décrivant le module
# 1. noyau Python (sys, time, math, ...)
# 2. modules tiers (numpy, pandas, matplotlib, PySide6, ...), en fait, ceux que vous avez dû installer manuellement avec pip install ...
# 3. vos propres modules 


# 1 ===========================================================================
# modules noyau Python, par exemple
import sys
# =============================================================================


# 2 ==========================================================================
# 2a 
# modules tiers AUTRES que PySide6, par exemple
import numpy as np

# 2b 
# poursuivre avec les modules PySide6 en 4 blocs :
# 2b1 : activer le __feature__ ainsi :

# -----------------------------------------------------------------------------
# Begin: Set Shiboken feature flags for Pythonic API. -------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------
# v--- begin all PySide6 imports ----------------------------------------------


# 2b2 : Faites ici vos importations PySide6 explicites, par exemple
from PySide6.QtCore import Qt, Signal, Slot, Property
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
# ...


# 2b3 : Ajouter ces lignes pour s'assurer que les fonctionnalités sont bien activées
#       On remarque le commentaire de fin de ligne pour éviter l'erreur d'importation non trouvée dans l'IDE.

# ^--- end all PySide6 imports ------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()
# End: Shiboken API style is now locked. --------------------------------------
# -----------------------------------------------------------------------------
# v--- if needed, begin all custom PySide6 imports ----------------------------


# 2b4 : importer vos modules PySide6 personnalisés, par exemple
import my_awesome_widget
# =============================================================================


# 3 ===========================================================================
# importer vos propres modules, par exemple
import my_module
import my_class
import my_function
# =============================================================================

```

Voici un exemple de code :
```python

import sys

import numpy as np


# -----------------------------------------------------------------------------
# Begin: Set Shiboken feature flags for Pythonic API. -------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------
# v--- begin all PySide6 imports ----------------------------------------------

from PySide6.QtCore import Slot, Signal, QMargins
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

# ^--- end all PySide6 imports ------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert 'snake_case' in feature.info() and 'true_property' in feature.info()
# End: Shiboken API style is now locked. --------------------------------------
# -----------------------------------------------------------------------------
# v--- if needed, begin all custom PySide6 imports ----------------------------


from scroll_image import ScrollImage, SolidColorIllustrator


# ...

```


### Régénération des Stubs IDE

Pour que votre éditeur de code offre une autocomplétion correcte avec les syntaxes modernes comme _snake_case_ et _true_property_, il faut régénérer les fichiers _stubs_ de PySide6.

Ces fichiers _stubs_ (`.pyi`) agissent comme un plan détaillé de la bibliothèque, et la commande suivante les met à jour pour que votre éditeur reconnaisse ces fonctionnalités et vous propose les bonnes suggestions. Exécuter cette commande dans votre terminal :

`pyside6-genpyi all --feature snake_case true_property`

Si pour une raison ou une autre vous désirez revenir à la syntaxe classique de PySide6, vous pouvez régénérer les stubs sans les fonctionnalités modernes en utilisant :

`pyside6-genpyi all`

## Stratégies de débogage

### Disposition inadéquate des widgets

Si vous constatez que vos widgets ne s'affichent pas correctement ou que la disposition semble incorrecte, l'utilisation de ces outils peut aider à mieux comprendre le problème et à le résoudre :
- concernant les QWidget :
    - taille (size)   
    - taille minimale (minimum_size)
    - taille maximale (maximum_size)
    - la méthode `size_hint` et `minimum_size_hint()` (attention, si on veut changer ces valeurs, il faut surcharger la méthode dans une sous-classe)
    - politique de redimensionnement (size_policy)
- concernant les layouts (QLayout) :
    - marges (contents_margins)
    - espacements (spacing)
    - l'étirement (stretch)
    - la méthode `invalidate()` pour forcer le recalcul du layout


Parfois, l'affichage de bordure autour des widgets peut aider à visualiser leur taille et leur position dans le layout. Voici un exemple de code illustrant l'utilisation de ces outils pour diagnostiquer et corriger les problèmes de disposition des widgets :
```python

widget = QWidget()
layout = QVBoxLayout()

layout.contents_margins = QContentsMargins(10, 5, 20, 15)  # Marges de gauche, haut, droite, bas
layout.spacing = 10  # Espacement entre les widgets dans le layout

widget.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Politique de redimensionnement lorsque les layouts doivent être recalculés
widget.style_sheet = "border: 1px solid green;"  # Affiche une bordure verte
```


