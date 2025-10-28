import sys
import os

from types import NoneType
from enum import Enum, auto
from random import uniform, randint, choice
from klustr_main import Ui_klustr3DDataWidget
import numpy as np


# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtGui import QVector3D, QColor, QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QGroupBox, QLabel, QSplitter, QScrollArea, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Slot, Signal, Qt, QTimer, QSize,QMargins
from PySide6.QtDataVisualization import Q3DScatter, QScatter3DSeries

# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------


from color_sequence import QColorSequence

class QScatter3dViewer(QWidget):
    """
    QScatter3dViewer est une classe héritant de QWidget et encapsule un usage 
    facile de la classe Q3DScatter. Elle permet la visualisation de données 
    3D sous forme de nuages de points.
    
    Cette classe fournit une interface de programmation gérant les séries de 
    données, les axes, les ombres et une rotation automatique.
    
    De plus, le widget offre un ensemble de fonctionnalités interactives avec 
    l'usage du clavier et de la souris (bouton droit + molette).
    
    La description suivante correspond à l'interface de programmation publique :
    
    Types:
    - ShadowType            Une énumération définissant les types d'ombres disponibles.
    - Axis                  Une classe imbriquée pour la gestion des axes.
    - Series                Une classe imbriquée pour la gestion des séries de données. TO DO à tester...
        
    Propriétés:
    - title                 Acccesseur et mutateur du titre principal.
    - shadow                Acccesseur et mutateur du type d'ombre utilisé.
    - auto_rotate           Acccesseur et mutateur de la rotation automatique de la scène 3D.
    - axis_[x|y|z].title    Obtenir ou définir le titre de l'axe concerné (x, y ou z).
    - axis_[x|y|z].range    Acccesseur et mutateur de l'étendu de l'axe concerné (x, y ou z).
    - series_count          Acccesseur du nombre de séries de données affichées.

    Méthodes:
    __init__                Constructeur du widget 3D.
    add_random_serie        Ajouter une série de points générés aléatoirement.
    add_serie               Ajouter une série de points définis par l'utilisateur.
    clear                   Effacer toutes les séries de donnée.
    remove_serie            Retirer une série de points spécifiée par son index ou par son nom.    

    Example:
    Exemple d'utilisation de la classe QScatter3dViewer pour créer un nuage de points 3D :

    >>> viewer = QScatter3dViewer()
    >>> viewer.title = "Nuage de Points 3D"
    >>> viewer.auto_rotate = True
    >>> viewer.shadow = QScatter3dViewer.ShadowType.SoftEdge

    # Configuration des axes
    >>> viewer.axis_x.title = "Axe X"
    >>> viewer.axis_x.range = (0, 100)
    >>> viewer.axis_y.title = "Axe Y"
    >>> viewer.axis_y.range = (0, 100)
    >>> viewer.axis_z.title = "Axe Z"
    >>> viewer.axis_z.range = (0, 100)

    # Ajout d'une série
    >>> import numpy as np
    >>> from PySide6.QtGui import QColor
    >>> data3d = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    >>> viewer.add_serie(data3d, QColor("red"), title="Série 1")
    >>> viewer.add_random_serie(100, QColor("blue"), title="Série 2", size_percent=0.2)

    # Vérification du nombre de séries
    >>> print(viewer.series_count)
    2

    # Suppression de la série
    >>> viewer.remove_serie(0) # by index
    >>> viewer.remove_serie('Série 2') # by name
    >>> print(viewer.series_count)
    0

    # Effacer toutes les séries
    >>> viewer.clear()

    """
    
    # public Types ------------------------------------------------------------

    class ShadowType(Enum):
        """
        L'énumération interne ShadowType permet de définir quel type d'ombres 
        utiliser dans la classe QScatter3dViewer.

        Attributes
        ----------
        NoShadow : Enum
            Représente l'absence d'ombre dans la visualisation 3D.
        Soft : Enum
            Représente une ombre adoucie.
        Hard : Enum
            Représente une ombre franche.

        Methods
        -------
        next:
            Méthode pour obtenir le type d'ombre suivant dans l'énumération.

        Example
        -------
        Exemple d'utilisation du type d'ombre dans la classe QScatter3dViewer :

        >>> viewer = QScatter3dViewer()
        >>> viewer.shadow = QScatter3dViewer.ShadowType.NoShadow  # Définir le type d'ombre comme 'NoShadow'
        >>> print(viewer.shadow)
        QScatter3dViewer.ShadowType.NoShadow

        # Obtenir le type d'ombre suivant
        >>> next_shadow = viewer.shadow.next
        >>> print(next_shadow)
        QScatter3dViewer.ShadowType.Soft

        # Appliquer le type d'ombre suivant
        >>> viewer.shadow = next_shadow
        """        
        NoShadow = auto()
        Soft = auto()
        Hard = auto()
        
        @property
        def next(self):
            members = list(self.__class__)
            actual_index = members.index(self)
            next_index = (actual_index + 1) % len(members)
            return members[next_index]
        
    class Axis:
        """
        La classe interne Axis offre une gestion simplifiée des axes de la 
        classe QScatter3dViewer.

        Cette classe sert d'interface pour configurer les propriétés d'un axe 
        individuel, telles que le titre et la plage. Elle correspond au patron 
        de conception Façade.

        Attributes
        ----------
        title : Optional[str]
            Le titre de l'axe. 
            None si le titre n'est pas visible.
        range : Optional[tuple[float, float]]
            La plage des valeurs de l'axe sous forme de tuple (min, max). 
            None si la plage est ajustée automatiquement.

        Methods
        -------
        __init__(axis):
            Initialise l'objet Axis avec l'axe donné.

        Example
        -------
        Exemple d'utilisation de la classe Axis pour effectuer la configurer 
        des axes :

        >>> viewer = QScatter3dViewer()
        # Configurer le titre de l'axe X
        >>> viewer.axis_x.title = "Axe X"
        >>> print(viewer.axis_x.title)
        "Axe X"

        # Configurer la plage de l'axe X
        >>> viewer.axis_x.range = (0, 100)
        >>> print(viewer.axis_x.range)
        (0, 100)

        # Retirer le titre et mettre la plage en ajustement automatique
        >>> viewer.axis_x.title = None
        >>> viewer.axis_x.range = None
        >>> print(viewer.axis_x.title)
        None
        >>> print(viewer.axis_x.range)
        None

        Note
        ----
        Les méthodes et propriétés de cette classe sont principalement 
        destinées à être utilisées par la classe parent QScatter3dViewer.
        """
                
        def __init__(self, axis):
            self.__axis = axis
            
        @property
        def title(self) -> str | None:
            """Le titre de l'axe. 
            
            Si la valeur est None, le titre n'est pas visible."""
            return self.__axis.title if self.__axis.title_visible else None
            
        @title.setter
        def title(self, value : str | None) -> None:
            if not isinstance(value, (str, NoneType)):
                raise TypeError('value must be a string or None')
            if value is None:
                self.__axis.title = ''
                self.__axis.title_visible = False
            else:
                self.__axis.title = value
                self.__axis.title_visible = True

        @property
        def range(self) -> tuple[float] | None:
            """La plage des valeurs de l'axe sous forme de tuple (min, max). 
            
            Si la valeur est None, la plage est ajustée automatiquement."""
            return None if self.__axis.auto_adjust_range else (self.__axis.min, self.__axis.max)

        @range.setter
        def range(self, value : tuple[int|float] | list[int|float] | None) -> None:
            if value is None:
                self.__axis.set_range(0.0, 1.0)
                self.__axis.auto_adjust_range = True
            else:
                if not isinstance(value, (tuple, list)) or len(value) != 2 or not all([isinstance(element, (float, int)) for element in value]) or value[1] < value[0]:
                    raise TypeError('value must be a tuple or list of two floats or integers with first < second')
                self.__axis.set_range(value[0], value[1])
                self.__axis.auto_adjust_range = False
                
    
    # # CES CLASSES N'ONT AUCUNEMENT ÉTÉ TESTÉES... TO DO!!!
    # class Series:
        
    #     def __init__(self, scatter : QScatter3DSeries) -> None:
    #         self.__scatter = scatter
            
    #     def __len__(self) -> int:
    #         return self.__scatter.data_proxy.item_count
        
    #     def __getitem__(self, key : int) -> np.ndarray[float]:
    #         return QScatter3dViewer.Serie(self.__scatter, key)
        
    #     def __delitem__(self, key : int) -> None:
    #         self.__scatter.remove_item(key)
        
        
    # class Serie:
    #     """Classe facilitant la gestion des séries de données dans QScatter3dViewer.
        
    #     Cette classe permet de manipuler les séries de données 3D dans le
    #     QScatter3dViewer. Elle offre des méthodes pour accéder et modifier les
    #     points de la série, ainsi que pour gérer les propriétés de la série
    #     comme le nom, la couleur et la visibilité.
        
    #     Cette classe est une autre façade pour la classe QScatter3DSeries de Qt."""
        
    #     def __init__(self, scatter : QScatter3DSeries, index : int) -> None:
    #         self.__scatter = scatter
    #         self.__index = index
            
    #     @property
    #     def name(self) -> str:
    #         """Le nom de la série."""
    #         return self.__scatter.title
        
    #     @name.setter
    #     def name(self, value : str) -> None:
    #         self.__scatter.title = value
            
    #     @property
    #     def color(self) -> QColor:
    #         """La couleur de la série."""
    #         return self.__scatter.base_color
        
    #     @color.setter
    #     def color(self, value : QColor) -> None:
    #         self.__scatter.base_color = value
            
    #     @property
    #     def visible(self) -> bool:
    #         """Spécifie si la série est visible ou non."""
    #         return self.__scatter.visible
        
    #     @visible.setter
    #     def visible(self, value : bool) -> None:
    #         self.__scatter.visible = value
        
    #     def __get_index(self, index: int) -> int:
    #         """Retourne l'index ajusté pour les séries de données en tenant compte des indexes négatifs."""
    #         return index if index >= 0 else self.__scatter.data_proxy.item_count + index
        
    #     def __getitem__(self, key : int) -> np.ndarray[float]:
    #         """Retourne les coordonnées 3D du point spécifié par l'index."""
    #         value3d : QVector3D = self.__scatter.data_proxy.items[self.__get_index(key)]
    #         return np.array([value3d.x(), value3d.y(), value3d.z()])
        
    #     def __setitem__(self, key : int, value : np.ndarray[float]) -> None:
    #         """Définit les coordonnées 3D du point spécifié par l'index."""
    #         self.__scatter.data_proxy.items[self.__get_index(key)] = QVector3D(*value)




    # private API -------------------------------------------------------------
    
    __tool_tip = f'''
<h4>Interactive action</h4>
<hr>
<h4>Keyboard's shortcuts</h4>
<span style='font-family: "Courier New", Courier, monospace;'>SPACE</span> : Toggle auto-rotation<br>
<span style='font-family: "Courier New", Courier, monospace;'>ENTER</span> : Reset auto-rotation speed<br>
<span style='font-family: "Courier New", Courier, monospace;'>&nbsp;&nbsp;+&nbsp;&nbsp;</span> : Increase rotation speed counterclockwise<br>
<span style='font-family: "Courier New", Courier, monospace;'>&nbsp;&nbsp;-&nbsp;&nbsp;</span> : Increase rotation speed clockwise<br>
<span style='font-family: "Courier New", Courier, monospace;'>&nbsp;&nbsp;&lt;&nbsp;&nbsp;</span> : Rotate left<br>
<span style='font-family: "Courier New", Courier, monospace;'>&nbsp;&nbsp;>&nbsp;&nbsp;</span> : Rotate right<br>
<span style='font-family: "Courier New", Courier, monospace;'>&nbsp;&nbsp;^&nbsp;&nbsp;</span> : Rotate up<br>
<span style='font-family: "Courier New", Courier, monospace;'>&nbsp;&nbsp;v&nbsp;&nbsp;</span> : Rotate down<br>
<span style='font-family: "Courier New", Courier, monospace;'>SHIFT</span> : Use SHIFT to rotate faster<br>
<span style='font-family: "Courier New", Courier, monospace;'>CTRL&nbsp;</span> : Use CONTROL to rotate even faster<br>
<h4>Mouse activities</h4>
<span style='font-family: "Courier New", Courier, monospace;'>RIGHT CLICK + MOVE</span> : Rotation manuelle<br>
<span style='font-family: "Courier New", Courier, monospace;'>WHEELE{'&nbsp;' * 12}</span> : Zoom in/out<br>
'''
    __shadow_mapping = { 
            ShadowType.NoShadow: Q3DScatter.ShadowQualityNone,
            ShadowType.Soft: Q3DScatter.ShadowQualitySoftHigh,
            ShadowType.Hard: Q3DScatter.ShadowQualityHigh }        

    ____registered_series = []
    @staticmethod
    def __create_serie():
        '''Le problème sous-jacent est lié à l'interaction entre la gestion de la 
        mémoire de Python et celle de la bibliothèque Qt, plus précisément entre 
        les classes `Q3DScatter` et `QScatter3DSeries` de PySide6 ou PyQt. En 
        Python, le garbage collector est principalement responsable de la gestion 
        de la durée de vie des objets, en se basant sur un comptage de références. 
        Cependant, dans le cas de Qt, la gestion de la durée de vie des objets est 
        souvent assurée par le framework lui-même, notamment via un système de 
        parentage d'objets.

        Si une instance de `QScatter3DSeries` est créée et ajoutée à une instance 
        de `Q3DScatter` mais qu'aucune référence explicite à cette série n'est 
        conservée dans le code Python, il est possible que le garbage collector de
        Python décide de récupérer cette instance, alors même que l'objet 
        sous-jacent en C++ reste utilisé par Qt. Ce comportement peut conduire à 
        des comportements indéfinis ou à des erreurs d'exécution, car l'objet en 
        C++ essaiera d'accéder à des ressources qui ont été libérées par Python.

        Pour pallier à ce problème, la classe `QScatter3DSeriesRegisterer` utilise 
        une variable de classe privée statique, `__registered_series`, pour 
        conserver des références explicites aux instances de `QScatter3DSeries` 
        créées. Cela empêche le garbage collector de Python de les récupérer 
        prématurément, tout en respectant les principes d'encapsulation et de 
        cohérence en regroupant cette logique de gestion de la durée de vie au 
        sein d'une classe dédiée.'''
        series = QScatter3DSeries()
        QScatter3dViewer.____registered_series.append(series)
        return series
    
    @staticmethod
    def __clear_series():
        QScatter3dViewer.____registered_series.clear()
        
    @staticmethod
    def __clamp(value : any, minimum : any, maximum : any) -> any:
        return max(minimum, min(value, maximum))
        
    @staticmethod
    def __map_value(value, input_min, input_max, output_min, output_max):
        return (value - input_min) / (input_max - input_min) * (output_max - output_min) + output_min
    
    @staticmethod
    def __set_font(widget : QWidget, bold : bool = False, italic : bool = False, point_size_ratio : float = 1.0):
        font = widget.font
        font.set_bold(bold)
        font.set_italic(italic)
        font.set_point_size(font.point_size() * point_size_ratio)
        widget.font = font

    def __rotate_x_axis(self, x_increment : float) -> None:
        camera = self.__scatter.scene.active_camera
        camera.x_rotation = (camera.x_rotation + x_increment) % 360.0
        
    def __rotate_y_axis(self, y_increment : float) -> None:
        camera = self.__scatter.scene.active_camera
        camera.y_rotation = (camera.y_rotation + y_increment) % 90.0
        
    def __update_legend(self) -> str:
        if self.series_count == 0:
            formatted_items = "<span style='font-style:italic;'>No series</span>"
        else:
            format_item = lambda serie_item: f"<p style='left-top: 25px;margin-top: 5px;margin-bottom: 5px;'><span style='border: 2px solid {serie_item.base_color.darker(400).name()};background-color:{serie_item.base_color.name()};display:inline-block;'>{'&nbsp;' * 4}</span>&nbsp;{serie_item.title} [{serie_item.data_proxy.item_count}]</p>" # line-height & border are not suported with QLabel yet
            formatted_items = ''.join([format_item(serie) for serie in self.__scatter.series_list()])
        
        legend = f"<p style='font-weight:600;margin-bottom:0'>Legend</p><p style='margin-top:0;margin-bottom:0'><em>{self.series_count} serie{'s' if self.series_count > 1 else ''}</em></p><hr>" + formatted_items
        self.__legend.text = legend
        
    def __remove_serie_by_index(self, index : int) -> bool:
        if index < 0 or index >= self.series_count:
            return False

        self.__scatter.remove_series(self.__scatter.series_list()[index])
        QScatter3dViewer.____registered_series.pop(index)
        self.__update_legend()
    
    def __remove_serie_by_name(self, name : str) -> bool:
        series_name = [serie.title for serie in self.__scatter.series_list()]
        try:
            index = series_name.index(name)
            return self.__remove_serie_by_index(index)
        except:
            return False
        
    def __add_serie(self, data : list[QVector3D], color : QColor, title : str, size_percent : float) -> int:
        size_percent = QScatter3dViewer.__clamp(size_percent, 0.0, 1.0)
        size = QScatter3dViewer.__map_value(size_percent, 0.0, 1.0, 0.005, 0.5)
        series = QScatter3dViewer.__create_serie()
        series.base_color = color
        series.item_size = size
        series.data_proxy.add_items(data)
        series.title = title
        self.__scatter.add_series(series)
        
        self.__update_legend()
        
        return len(self.__scatter.series_list()) - 1
    

    # public API --------------------------------------------------------------

    def __init__(self, auto_rotate: bool = True, parent: QWidget = None):
        """
        Initialise la classe QScatter3dViewer.

        Initialise une nouvelle instance de la classe, avec la possibilité 
        d'activer ou de désactiver la rotation automatique du graphique 3D. 
        De plus, cette méthode permet de spécifier un widget parent si 
        nécessaire.

        Paramètres:
        - auto_rotate   Spécifie si la visualisation 3D doit être en rotation 
                        automatique. Par défaut à True, ce qui signifie que la 
                        rotation automatique est activée.
        - parent        Le widget parent auquel ce QScatter3dViewer sera 
                        associé. Par défaut à 'None', ce qui signifie que le 
                        'QScatter3dViewer' est un 'widget' indépendant.

        Exemple:
        >>> viewer = QScatter3dViewer()
        Initialise un viewer avec rotation automatique activée et sans parent.

        >>> viewer = QScatter3dViewer(auto_rotate=False, parent=un_widget_parent)
        Initialise un viewer sans rotation automatique et avec un widget parent 
        spécifié.
        """
        super().__init__(parent)
        
        # Création du widget interne 3D
        self.__scatter = Q3DScatter()
        self.__scatter_widget = QWidget.create_window_container(self.__scatter)
        self.__scatter_widget.minimum_size = QSize(400, 200)
        self.__scatter_widget.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        # Installation du filtre d'événement pour les actions clavier
        self.install_event_filter(self)
        self.__scatter.install_event_filter(self)

        # Création des éléments de l'interface utilisateur
        self.__title = QLabel('3D Scatter')
        self.__title.alignment = Qt.AlignCenter
        self.__title.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        QScatter3dViewer.__set_font(self.__title, bold = True, italic = False, point_size_ratio = 1.25)

        # Création de la légende
        self.__legend = QLabel()
        self.__legend.alignment = Qt.AlignLeft | Qt.AlignBottom
        self.__legend.text_format = Qt.RichText
        self.__legend.word_wrap = True
        self.__legend.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.__legend.set_style_sheet("QLabel { margin: 5px; }")
        QScatter3dViewer.__set_font(self.__legend, bold = False, italic = False, point_size_ratio = 0.925)
        self.__update_legend()
        
        # Création du widget de légende gérant le défilement vertical si nécessaire
        legend_scroll_area = QScrollArea()
        legend_scroll_area.widget_resizable = True
        legend_scroll_area.horizontal_scroll_bar_policy = Qt.ScrollBarAlwaysOff
        legend_scroll_area.vertical_scroll_bar_policy = Qt.ScrollBarAsNeeded
        legend_scroll_area.set_widget(self.__legend)
        legend_scroll_area.minimum_width = 115
        
        # Création du layout principal avec séparation horizontale pour gérer la séparation entre le graphique 3d et la légende
        legend_splitter = QSplitter()
        legend_splitter.orientation = Qt.Horizontal
        legend_splitter.add_widget(self.__scatter_widget)
        legend_splitter.add_widget(legend_scroll_area)
        
        # Création du layout principal
        layout = QVBoxLayout()
        layout.add_widget(self.__title)
        layout.add_widget(legend_splitter)
        self.set_layout(layout)
        
        # Configuration de la vue 3d
        camera = self.__scatter.scene.active_camera
        camera.zoom_level = 85.0 # camera.zoom_level - 15.0
        camera.y_rotation = 30.0
        
        # Configuration de l'effet d'ombrage
        self.shadow = QScatter3dViewer.ShadowType.NoShadow
        
        # Création du mécanisme de rotation automatique
        self.__timer = QTimer()
        self.__timer.timeout.connect(lambda : self.__rotate_x_axis(-self.__auto_rotate_speed))
        self.__auto_rotate_speed = -0.1
        self.auto_rotate = auto_rotate
        
        # Configuration du tool tip
        self.tool_tip = QScatter3dViewer.__tool_tip

    # override
    def event_filter(self, watched, event):
        """
        Filtre d'événement personnalisé pour le widget QScatter3dViewer.

        Cette méthode est utilisée pour intercepter et traiter les événements 
        spécifiques liés au widget QScatter3dViewer. Elle n'est pas destinée 
        à être utilisée comme fonction publique standard de la classe.
        
        Dans le contexte de la méthode event_filter, le but est de fournir une 
        implémentation spécifique pour le traitement des événements au sein de 
        la classe QScatter3dViewer. En Python, le mot-clé "override" n'est pas 
        explicitement utilisé, mais le mécanisme sous-jacent est le même : la 
        méthode dans la classe dérivée remplace la méthode de la classe de base 
        (dans ce cas, QWidget), permettant ainsi à la classe dérivée de gérer 
        les événements de manière personnalisée. Ce remplacement de méthodes 
        est souvent utilisé pour étendre ou modifier les comportements définis 
        dans les classes parentes.        

        Paramètres
        ----------
        watched : QObject
            L'objet qui est surveillé pour des événements.
            
        event : QEvent
            L'événement qui a été envoyé à l'objet surveillé.

        Note
        ----
        Cette méthode n'est pas destinée à être utilisée directement via 
        l'API publique de la classe.
        """        
        if event.type() == QKeyEvent.KeyPress:
            if event.modifiers() == Qt.ShiftModifier:
                multiplier = 1.25
            elif event.modifiers() == Qt.ControlModifier:
                multiplier = 5.0
            elif event.modifiers() == (Qt.ShiftModifier | Qt.ControlModifier): # < do not work with match
                multiplier = 10.0
            else:
                multiplier = 0.25

            match event.key():
                case Qt.Key_Space:
                    self.auto_rotate = not self.auto_rotate
                case Qt.Key_Plus:
                    self.__auto_rotate_speed = QScatter3dViewer.__clamp(self.__auto_rotate_speed - 0.1 * multiplier, -2.5, 2.5)
                case Qt.Key_Minus:
                    self.__auto_rotate_speed = QScatter3dViewer.__clamp(self.__auto_rotate_speed + 0.1 * multiplier, -2.5, 2.5)
                case Qt.Key_Return:
                    self.__auto_rotate_speed = -0.1
                case Qt.Key_Left:
                    if self.auto_rotate: self.auto_rotate = False
                    self.__rotate_x_axis(-0.5 * multiplier)
                case Qt.Key_Right:
                    if self.auto_rotate: self.auto_rotate = False
                    self.__rotate_x_axis(0.5 * multiplier)
                case Qt.Key_Up:
                    if self.auto_rotate: self.auto_rotate = False
                    self.__rotate_y_axis(-0.5 * multiplier)
                case Qt.Key_Down:
                    if self.auto_rotate: self.auto_rotate = False
                    self.__rotate_y_axis(0.5 * multiplier)
                case Qt.Key_S:
                    self.shadow = self.shadow.next
                case _ :
                    return super().event_filter(watched, event)
            
            return True
        
        return super().event_filter(watched, event)   

    @property
    def title(self) -> str:
        """
        Le titre du graphique. [Lecture et écriture]
         
        Le titre est affiché en haut du graphique 3d. Si le titre assigné est 
        vide, la valeur par défaut est assignée.
        
        Le titre par défaut est '3D Scatter'.
            
        Exceptions:
            TypeError: si la valeur définie n'est pas une chaîne de caractères.
        """        
        return self.__title.text
    
    @title.setter
    def title(self, value : str) -> None:
        if not isinstance(value, str):
            raise TypeError('title must be a string')
        if len(value) == 0:
            value = '3D Scatter'
        self.__title.text = value
        
    @property
    def shadow(self) -> ShadowType:
        """
        Le type d'ombre du viewer 3D. [Lecture et écriture]
        
        Le type d'ombre doit être une instance de l'énumération ShadowType 
        définie dans QScatter3dViewer.
        
        L'ombre par défaut est : QScatter3dViewer.ShadowType.NoShadow
        
        Exception:
            TypeError: si la valeur définie n'est pas une instance de ShadowType.
        """        
        return self.__shadow
    
    @shadow.setter
    def shadow(self, value : ShadowType) -> None:
        if not isinstance(value, QScatter3dViewer.ShadowType):
            raise TypeError('value must be a ShadowType object')

        self.__shadow = value
        self.__scatter.shadow_quality = QScatter3dViewer.__shadow_mapping[self.__shadow]
            
    @property
    def auto_rotate(self) -> bool:
        """
        État de la rotation automatique du viewer 3D. [Lecture et écriture]

        La valeur True indique que la rotation automatique est activée, tandis
        que la valeur False indique qu'elle est désactivée.
                
        La valeur par défaut est True.
            
        Exception:
            TypeError: si la valeur définie n'est pas un objet booléen.
        """
        return self.__auto_rotate
        
    @auto_rotate.setter
    def auto_rotate(self, value : bool) -> None:
        if not isinstance(value, bool):
            raise TypeError('value must be a boolean object')
        self.__auto_rotate = value
        if self.__auto_rotate:
            self.__timer.start(30)
        else:
            self.__timer.stop()
            
    @property
    def axis_x(self) -> Axis:
        """L'axe des abscisses du viewer 3D, l'axe X. [Lecture seule]"""        
        return QScatter3dViewer.Axis(self.__scatter.axis_x)
            
    @property
    def axis_y(self) -> Axis:
        """L'axe des ordonnées du viewer 3D, l'axe Y. [Lecture seule]"""        
        return QScatter3dViewer.Axis(self.__scatter.axis_y)
            
    @property
    def axis_z(self) -> Axis:
        """L'axe de la profondeur du viewer 3D, l'axe Z. [Lecture seule]"""     
        return QScatter3dViewer.Axis(self.__scatter.axis_z)
    
    # @property
    # def series(self) -> Series:
    #     """La série de données du viewer 3D. [Lecture seule]"""
    #     return QScatter3dViewer.Series(self.__scatter.series_list()[0])
    
    @property
    def series_count(self):
        """Le nombre total de séries de données présentes du viewer 3d. [Lecture seule]"""
        return len(self.__scatter.series_list())

    def add_random_serie(self, n_points : int, color : QColor, title : str = '', size_percent : float = 0.25) -> int:
        """
        Ajoute une série de points générés aléatoirement.

        Paramètres:
            n_points (int): Nombre de points à générer.
            color (QColor): Couleur des points.
            title (str, optionnel): Titre de la série. Par défaut vide.
            size_percent (float, optionnel): Taille relative des points exprimée en pourcentage. Par défaut à 0,25.

        Retourne:
            int: Identifiant de la série ajoutée correspondant à son indexe 
                 lors de l'insertion. Attention, si des séries sont retirées, 
                 cet identifiant n'est plus pertinent.

        Exception:
            TypeError: si les types des arguments ne sont pas ceux attendus.
        """        
        n_points = max(1, n_points)
        return self.__add_serie([QVector3D(uniform(0.0, 1.0), uniform(0.0, 1.0), uniform(0.0, 1.0)) for _ in range(n_points)], color, title, size_percent)
    
    def add_serie(self, data3d : np.ndarray[float], color : QColor, title : str = '', size_percent : float = 0.25) -> int:
        """
        Ajoute une série de points spécifiés.

        Paramètres:
            data3d (np.ndarray[float]): Tableau NumPy contenant les 
                                        coordonnées 3D des points 
                                        (forme 3 x n ou n x 3).
            color (QColor): Couleur des points.
            title (str, optionnel): Titre de la série. Par défaut vide.
            size_percent (float, optionnel): Taille relative des points 
                                             exprimée en pourcentage. 
                                             Par défaut à 0,25.

        Retourne:
            int: Identifiant de la série ajoutée correspondant à son indexe 
                 lors de l'insertion. Attention, si des séries sont retirées, 
                 cet identifiant n'est plus pertinent.

        Exceptions:
            TypeError: si `data3d` n'est pas une instance de ndarray de NumPy.
            ValueError: si `data3d` ne respecte pas les contraintes de forme 
                        (doit être un tableau de forme 3 x n ou n x 3).
        """        
        if not isinstance(data3d, np.ndarray):
            raise TypeError('data3d must be a NumPy ndarray instance') 
        if data3d.ndim != 2 or 3 not in data3d.shape:
            raise ValueError(f'data3d must be a NumPy 2d ndarray instance of size 3 x n  or  n x 3 : the given array is a {data3d.ndim}d with a shape of {data3d.shape}.') 
        data = [QVector3D(x, y, z) for x, y, z in (data3d if data3d.shape[1] == 3 else data3d.T)]
        return self.__add_serie(data, color, title, size_percent)
    
    def remove_serie(self, index_or_name : int | str) -> bool:
        """
        Supprime une série de données par son index ou par son nom. 
        
        Si un nom est donné et que plusieurs séries portent le même nom, 
        seulement la première occurence est retirée.

        Paramètres:
            index_or_name (int | str): Index ou nom de la série à supprimer.

        Retourne:
            bool: `True` si la série a été supprimée avec succès, `False` sinon.

        Exception:
            TypeError: si `index_or_name` n'est ni un entier (index) ni une 
                       chaîne de caractères (nom).
        """
        if isinstance(index_or_name, int):
            return self.__remove_serie_by_index(index_or_name)
        elif isinstance(index_or_name, str):
            return self.__remove_serie_by_name(index_or_name)
        
        raise TypeError('index_or_name must be an integer (index) or a string (name).')
        
    def clear(self) -> None:
        """Supprime toutes les séries."""        
        for serie in self.__scatter.series_list():
            self.__scatter.remove_series(serie)
        QScatter3dViewer.__clear_series()
        self.__update_legend()
 




class KnnImageClassificationWidget(QWidget):
    """Widget pour la classification KNN avec visualisation 3D"""
    
    def __init__(self, klustr_dao, parent=None):
        super().__init__(parent)
        
        self.klustr_dao = klustr_dao
        
        # Créer le viewer 3D avec rotation automatique
        self.viewer_3d = QScatter3dViewer(auto_rotate=True)
        self.viewer_3d.title = "KNN Classification 3D"
        self.viewer_3d.axis_x.title = "Axis 1"
        self.viewer_3d.axis_y.title = "Axis 2"
        self.viewer_3d.axis_z.title = "Axis 3"
        
        # Créer le widget de contrôle (l'interface UI)
        self.control_widget = QWidget()
        # Tu devras importer Ui_klustrDataWidget depuis ton fichier principal
        
        self.ui = Ui_klustr3DDataWidget(klustr_dao)
        self.ui.setupUi(self.control_widget)
        
        # Fixer la largeur du panneau de contrôle
        self.control_widget.set_fixed_width(390)
        
        # Layout horizontal : contrôles à gauche, viewer 3D à droite
        layout = QHBoxLayout(self)
        layout.add_widget(self.control_widget)
        layout.add_widget(self.viewer_3d)
        layout.contents_margins = (QMargins(0, 0, 0, 0))
    
    def add_classification_data(self, data3d, color, title=''):
        """Ajoute des données de classification au viewer 3D"""
        self.viewer_3d.add_serie(data3d, color, title)