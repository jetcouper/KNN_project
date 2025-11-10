import sys
import klustr_3d as Animation
from KNN import KNNNumpy
from Axe1 import Axe1
from Axe2 import Axe2
from Axe3 import Axe3
import numpy as np
# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QSize,QRect,QMetaObject,QCoreApplication,QMargins
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import  (QApplication, QWidget, QListView, QTreeView,  
                                QGroupBox, QLabel, QCheckBox, QPlainTextEdit,
                                QGridLayout, QHBoxLayout, QVBoxLayout, QSplitter, QSizePolicy,
                                QMessageBox,QStackedWidget, QTabWidget,QComboBox,QPushButton,QScrollBar)
from PySide6.QtGui import  (QImage, QPixmap, QIcon, QPainter, QFont, QPen, QBrush, QColor, 
                            QStandardItemModel, QStandardItem,
                            QClipboard)
from color_sequence import QColorSequence


# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------


from db_credential import PostgreSQLCredential
from klustr_dao import PostgreSQLKlustRDAO
from klustr_utils import QtNpConvert


#     ___  _       _ _                          __                      _      _     
#    / _ \| |_    (_) |_ ___ _ __ ___  ___     / /  _ __ ___   ___   __| | ___| |___ 
#   | | | | __|   | | __/ _ \ '_ ` _ \/ __|   / /  | '_ ` _ \ / _ \ / _` |/ _ \ / __|
#   | |_| | |_    | | ||  __/ | | | | \__ \  / /   | | | | | | (_) | (_| |  __/ \__ \
#    \__\_\\__|   |_|\__\___|_| |_| |_|___/ /_/    |_| |_| |_|\___/ \__,_|\___|_|___/
#                                                                                    




class KlustRDatasetModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def update(self, klustr_dao):
        self.clear()
        self.set_horizontal_header_labels(['Name', 'Translation', 'Rotation', 'Scaling', 'Label count', 'Image count'])

        total_label_image_count = klustr_dao.total_label_image_count
        label_count = total_label_image_count[0][0]
        image_count = total_label_image_count[0][1]
        self.append_row([
                    KlustRDatasetItem(-1, 'All available images'),
                    QStandardItem('-'), 
                    QStandardItem('-'), 
                    QStandardItem('-'), 
                    QStandardItem(f'{label_count}'),
                    QStandardItem(f'{image_count}')])

        for dataset in klustr_dao.available_datasets:
            translated = 'true' if dataset[2] else 'false'
            rotated = 'true' if dataset[3] else 'false'
            scaled = 'true' if dataset[4] else 'false'
            label_count = f'{dataset[5]}'
            training_image_count = f'{dataset[6]}'
            test_image_count = f'{dataset[7]}'
            image_count = f'{dataset[8]}'
            self.append_row([
                    KlustRDatasetItem(dataset[0], dataset[1], translated, rotated, scaled, label_count, training_image_count, test_image_count),
                    QStandardItem(translated), 
                    QStandardItem(rotated), 
                    QStandardItem(scaled), 
                    QStandardItem(label_count),
                    QStandardItem(image_count)]
                    )

    # def flags(self, index):
    #     item = index.model().item_from_index(index)
    #     if isinstance(item, KlustRDatasetItem) and id != -1:
    #         return super().flags(index) & ~Qt.ItemIsSelectable
    #     else:
    #         return super().flags(index)


class KlustRLabelItem(QStandardItem):
    def __init__(self, id, name, thumbnail):
        self._id = id
        self._name = name

        img = QtNpConvert.qimage_from_png(thumbnail)
        self._thumbnail_icon = QIcon() if img.is_null() else QIcon(QPixmap.from_image(img))

        super().__init__(self._thumbnail_icon, self._name)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

class KlustRLabelModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def _update(self, dataset):
        sb = QtCore.QSignalBlocker(self)
        self.clear()
        sb.unblock()
        for image_label in dataset:
            self.append_row(KlustRLabelItem(image_label[0], image_label[1], image_label[2]))

    def update_for_all_images(self, klustr_dao):
        self._update(klustr_dao.available_labels)

    def update_from_dataset(self, dataset_name, klustr_dao):
        self._update(klustr_dao.labels_from_dataset(dataset_name))

class KlustRImageItem(QStandardItem):

    def __init__(self, label_id, image_id, name, width, height, image, thumbnail, transformation):
        self._label_id = label_id
        self._image_id = image_id
        self._name = name
        self._width = width
        self._height = height
        self._translated = transformation[0] == '1'
        self._rotated = transformation[1] == '1'
        self._scaled = transformation[2] == '1'

        img = QtNpConvert.qimage_from_png(thumbnail)
        self._thumbnail_icon = QIcon() if img.is_null() else QIcon(QPixmap.from_image(img))

        img = QtNpConvert.qimage_from_png(image)
        self._image = QIcon() if img.is_null() else img

        # pour obtenir matrice des img
        self._np_image = None
        if not img.is_null():
            self._np_image = QtNpConvert.np_from_qimage(img)
            
        super().__init__(self._thumbnail_icon, self._name)

    @property #ajout comme property
    def np_image(self):
        return self._np_image
    @property
    def label_id(self):
        return self._label_id

    @property
    def image_id(self):
        return self._image_id

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def image(self):
        return self._image

    @property
    def translated(self):
        return self._translated

    @property
    def rotated(self):
        return self._rotated

    @property
    def scaled(self):
        return self._scaled


class KlustRImageModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._label_id = None

    def _update(self, images):
        sb = QtCore.QSignalBlocker(self)
        self.clear()
        sb.unblock()
        for image_info in images:
            # label_id, image_id, name, width, height, image, thumbnail, transformation
            new_item = KlustRImageItem(image_info[0], image_info[2], image_info[3], image_info[4], image_info[5], image_info[6], image_info[7], image_info[11])
            self.append_row(new_item)

    def update_for_all_images(self, klustr_dao, label_id, translated, rotated, scaled, exclusive):
        klustr_dao.set_transformation_filters(translated, rotated, scaled, exclusive)
        self._update(klustr_dao.image_from_label(label_id))

    def update_from_dataset(self, klustr_dao, dataset_name, label_id, training_image):
        self._update(klustr_dao.image_from_dataset_label(dataset_name, label_id, training_image))

    def load_all_np_images(self):
        pass
        
class ColoredWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._brush = QBrush(Qt.white)
        self._pen = QPen(Qt.black, 1.)

    @property
    def brush(self):
        return self._brush

    @brush.setter
    def brush(self, value):
        self._brush = value
        self.update()

    @property
    def pen(self):
        return self._pen

    @pen.setter
    def pen(self, value):
        self._pen = value
        self.update()

    def paint_event(self, event):
        painter = QPainter(self)
        painter.set_brush(self.brush)
        painter.set_pen(self.pen)
        painter.draw_rect(self.rect)



#    _  ___           _   ____  ___                            ___        __    __        ___     _            _   
#   | |/ / |_   _ ___| |_|  _ \|_ _|_ __ ___   __ _  __ _  ___|_ _|_ __  / _| __\ \      / (_) __| | __ _  ___| |_ 
#   | ' /| | | | / __| __| |_) || || '_ ` _ \ / _` |/ _` |/ _ \| || '_ \| |_ / _ \ \ /\ / /| |/ _` |/ _` |/ _ \ __|
#   | . \| | |_| \__ \ |_|  _ < | || | | | | | (_| | (_| |  __/| || | | |  _| (_) \ V  V / | | (_| | (_| |  __/ |_ 
#   |_|\_\_|\__,_|___/\__|_| \_\___|_| |_| |_|\__,_|\__, |\___|___|_| |_|_|  \___/ \_/\_/  |_|\__,_|\__, |\___|\__|
#                                                   |___/                                           |___/          

class KlustRImageInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.focus_policy = Qt.StrongFocus

        self.view_label = QLabel()
        self.view_label.style_sheet = 'QLabel { background-color : #313D4A; padding : 10px 10px 10px 10px; }' # 354A64
        self.view_label.alignment = Qt.AlignCenter

        self.red_color = QColor(205, 65, 65)
        self.green_color = QColor(65, 205, 82)

        transf_widget_size = QSize(28, 12)
        self.translated_widget = ColoredWidget()
        self.rotated_widget = ColoredWidget()
        self.scaled_widget = ColoredWidget()
        self.translated_widget.set_fixed_size(transf_widget_size)
        self.rotated_widget.set_fixed_size(transf_widget_size)
        self.scaled_widget.set_fixed_size(transf_widget_size)
        self.translated_widget.tool_tip = 'translation was applied'
        self.rotated_widget.tool_tip = 'rotation was applied'
        self.scaled_widget.tool_tip = 'scaling was applied'
        self.translated_widget.brush = QBrush(self.green_color)
        self.rotated_widget.brush = QBrush(self.red_color)
        self.scaled_widget.brush = QBrush(self.green_color)
        transformation_layout = QHBoxLayout()
        transformation_layout.add_stretch()
        transformation_layout.add_widget(self.translated_widget)
        transformation_layout.add_widget(self.rotated_widget)
        transformation_layout.add_widget(self.scaled_widget)
        transformation_layout.add_stretch()

        self.info = QPlainTextEdit()
        font = self.info.font
        font.set_family('Courier New') # monospace
        self.info.font = font
        self.info.read_only = True
        self.info.line_wrap_mode = QPlainTextEdit.NoWrap

        layout = QVBoxLayout(self)
        layout.add_widget(QLabel('Image information'))
        layout.add_widget(self.view_label)
        layout.add_layout(transformation_layout)
        layout.add_widget(self.info)
        layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)

    def key_press_event(self, event):
        clipboard = QClipboard()
        if event.key() == Qt.Key_Return:
            clipboard.set_pixmap(self.view_label.pixmap)
        elif event.key() == Qt.Key_Space:
            clipboard.set_text(self.info.plain_text)

    def update_info(self, image_item):
        def str_info(t, info, length=60):
            title = t + ' ' + '-' * (length - len(t) - 1)
            info = '\n'.join([f' - {k:<15} : {str(value)}' for k, value in info.items()])
            return title + '\n' + info + '\n'

        data_base_info = {
                'Image name': image_item.name,
                'Width' : image_item.width,
                'Height' : image_item.height,
                'Translated' : image_item.translated,
                'Rotated' : image_item.rotated,
                'Scaled' : image_item.scaled
            }
        image_info = {
                'Width' : image_item.image.width(),
                'Height' : image_item.image.height(),
                'Format' : image_item.image.format(),
                'Depth' : image_item.image.depth(),
                'Bytes per line' : image_item.image.bytes_per_line(),
                'Cache key' : hex(image_item.image.cache_key())
            }

        metadata_info = {k:image_item.image.text(k) for k in image_item.image.text_keys()}

        self.info.plain_text = str_info('From database', data_base_info) \
                                + str_info('From image', image_info) \
                                + str_info('From meta data', metadata_info)
        self.view_label.pixmap = QPixmap.from_image(image_item.image)

        self.translated_widget.brush = QBrush(self.green_color) if image_item.translated else QBrush(self.red_color)
        self.rotated_widget.brush = QBrush(self.green_color) if image_item.rotated else QBrush(self.red_color)
        self.scaled_widget.brush = QBrush(self.green_color) if image_item.scaled else QBrush(self.red_color)



#    _  ___           _   ____  ____        _        ____                         __     ___              __        ___     _            _   
#   | |/ / |_   _ ___| |_|  _ \|  _ \  __ _| |_ __ _/ ___|  ___  _   _ _ __ ___ __\ \   / (_) _____      _\ \      / (_) __| | __ _  ___| |_ 
#   | ' /| | | | / __| __| |_) | | | |/ _` | __/ _` \___ \ / _ \| | | | '__/ __/ _ \ \ / /| |/ _ \ \ /\ / /\ \ /\ / /| |/ _` |/ _` |/ _ \ __|
#   | . \| | |_| \__ \ |_|  _ <| |_| | (_| | || (_| |___) | (_) | |_| | | | (_|  __/\ V / | |  __/\ V  V /  \ V  V / | | (_| | (_| |  __/ |_ 
#   |_|\_\_|\__,_|___/\__|_| \_\____/ \__,_|\__\__,_|____/ \___/ \__,_|_|  \___\___| \_/  |_|\___| \_/\_/    \_/\_/  |_|\__,_|\__, |\___|\__|
#                                                                                                                             |___/          

class KlustRDataSourceViewWidget(QWidget):

    def __init__(self, klustr_dao, parent=None):
        
        super().__init__(parent)

        self.klustr_dao = klustr_dao
        if self.klustr_dao.is_available:
            self._setup_models()
            self._setup_gui()

            self._update_dataset()
            # self.label_model.update_for_all_images(self.pg_cursor)
            # self.image_label_list_view.set_current_index(self.label_model.index(0, 0))
            # self.image_list_view.set_current_index(self.image_model.index(0, 0))
        else:
            self._setup_invalid_gui()

    def _setup_models(self):
        self.dataset_model = KlustRDatasetModel()
        self.label_model = KlustRLabelModel()
        self.image_model = KlustRImageModel()

    def _setup_invalid_gui(self):
        not_available = QLabel('Data access unavailable')
        not_available.alignment = Qt.AlignCenter
        not_available.enabled = False
        layout = QGridLayout(self)
        layout.add_widget(not_available)
        QMessageBox.warning(self, 'Data access unavailable', 'Data access unavailable.')

    def _setup_gui(self):
        # setup 3 widget model view : QTreeView - QListView - QListView
        self.dataset_tree_view, self.dataset_count_label, dataset_widget = self._setup_view_widget(QTreeView(), 'Dataset', self.dataset_model, self.select_dataset, -1)
        self.image_label_list_view, self.image_label_count_label, image_label_widget = self._setup_view_widget(QListView(), 'Label', self.label_model, self.select_label)
        self.image_list_view, self.image_count_label, image_widget = self._setup_view_widget(QListView(), 'Image', self.image_model, self.select_image)

        # configure QTreeView
        self.dataset_tree_view.header_hidden = False
        self.dataset_tree_view.horizontal_scroll_mode = QTreeView.ScrollPerPixel
        self.dataset_tree_view.horizontal_scroll_bar_policy = Qt.ScrollBarAsNeeded
        self.dataset_tree_view.selection_mode = QTreeView.SingleSelection
        self.dataset_tree_view.edit_triggers = QtWidgets.QAbstractItemView.NoEditTriggers

        # setup image view widget
        self.image_info_widget = KlustRImageInfoWidget()

        # layouting main widget
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        view_layout.add_widget(dataset_widget)
        view_layout.add_widget(image_label_widget)
        view_layout.add_widget(image_widget)

        view_splitter = QSplitter()
        view_splitter.orientation = Qt.Horizontal
        view_splitter.add_widget(view_widget)
        view_splitter.add_widget(self.image_info_widget)
        view_splitter.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        # setup transformation filter widget
        self.filter_box = QGroupBox('Filter')
        self.filter_box.enabled = False

        self.translation_checkbox = QCheckBox('Translation')
        self.rotation_checkbox = QCheckBox('Rotation')
        self.scaling_checkbox = QCheckBox('Scaling')
        self.exclusive_checkbox = QCheckBox('Exclusive')

        self.translation_checkbox.checked = True
        self.rotation_checkbox.checked = True
        self.scaling_checkbox.checked = True
        self.exclusive_checkbox.checked = False

        # setup transformation filter widget
        filter_layout = QHBoxLayout(self.filter_box)
        filter_layout.add_widget(self.translation_checkbox)
        filter_layout.add_widget(self.rotation_checkbox)
        filter_layout.add_widget(self.scaling_checkbox)
        filter_layout.add_widget(self.exclusive_checkbox)
        filter_layout.add_stretch()

        # connect transformation filter widget
        self.translation_checkbox.stateChanged.connect(self._update_models)
        self.rotation_checkbox.stateChanged.connect(self._update_models)
        self.scaling_checkbox.stateChanged.connect(self._update_models)
        self.exclusive_checkbox.stateChanged.connect(self._update_models)

        # main layouting
        layout = QVBoxLayout(self)
        layout.add_widget(view_splitter)
        layout.add_widget(self.filter_box)

    def _setup_view_widget(self, view_widget, title, model, update_slot, width=250):
        view_widget.set_model(model)
        view_widget.selection_behavior = QtWidgets.QAbstractItemView.SelectRows
        view_widget.selection_model().selectionChanged.connect(update_slot)
        view_widget.edit_triggers = QtWidgets.QAbstractItemView.NoEditTriggers
        count_widget = QLabel()
        count_widget.alignment = Qt.AlignRight
        font = count_widget.font
        font.set_italic(True)
        count_widget.font = font
        widget = QWidget()
        if width > 0:
            widget.set_fixed_width(width)
        layout = QVBoxLayout(widget)
        layout.add_widget(QLabel(title))
        layout.add_widget(view_widget)
        layout.add_widget(count_widget)
        layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        return view_widget, count_widget, widget

    @Slot()
    def _update_dataset(self):
        self.dataset_model.update(self.klustr_dao)
        self.dataset_count_label.text  = f'''{self.dataset_model.row_count() - 1} datasets'''
        self.dataset_tree_view.set_current_index(self.dataset_model.index(0, 0))

    @Slot()
    def _update_models(self):
        self.image_model.update_for_all_images(self.label_model.item(0, 0).id,
                                self.pg_cursor,
                                self.translation_checkbox.checked,
                                self.rotation_checkbox.checked,
                                self.scaling_checkbox.checked,
                                self.exclusive_checkbox.checked)
        self.image_label_count_label.text  = f'''{self.label_model.row_count()} labels'''
        self.image_list_view.set_current_index(self.image_model.index(0, 0))

    def show_event(self, event):
        pass

    @Slot()
    def select_dataset(self, selected, deselected):
        if selected:
            index = selected.indexes()[0]
            item = index.model().item_from_index(index)
            if isinstance(item, KlustRDatasetItem):
                if item.id == -1:
                    self.label_model.update_for_all_images(self.klustr_dao)
                else:
                    self.dataset_tree_view.set_current_index(self.dataset_model.index(0, 0, index))
            else:
                self.label_model.update_from_dataset(item.parent().name, self.klustr_dao)
            self.image_label_list_view.set_current_index(self.label_model.index(0, 0))
            self.image_label_count_label.text  = f'''{self.label_model.row_count()} labels'''


    @Slot()
    def select_label(self, selected, deselected):
        if selected:
            dataset_index = self.dataset_tree_view.selection_model().selected_indexes[0]
            dataset_item = self.dataset_model.item_from_index(dataset_index)
            if isinstance(dataset_item, KlustRDatasetItem):
                self.image_model.update_for_all_images(
                                        self.klustr_dao, 
                                        self.label_model.item_from_index(selected.indexes()[0]).id, 
                                        self.translation_checkbox.checked,
                                        self.rotation_checkbox.checked,
                                        self.scaling_checkbox.checked,
                                        self.exclusive_checkbox.checked)
            else:
                training = dataset_index.row() == 0
                dataset_index = self.dataset_tree_view.selection_model().selected_indexes[0].parent()
                dataset_item = self.dataset_model.item_from_index(dataset_index)
                label_index = self.image_label_list_view.selection_model().selected_indexes[0]
                label_item = self.label_model.item_from_index(label_index)
                self.image_model.update_from_dataset(self.klustr_dao, dataset_item.name, label_item.id, training)
            self.image_list_view.set_current_index(self.image_model.index(0, 0))
            self.image_count_label.text  = f'''{self.image_model.row_count()} images'''

    @Slot()
    def select_image(self, selected, deselected):
        if selected:
            self.image_info_widget.update_info(self.image_model.item_from_index(selected.indexes()[0]))

    # def get_all_np_images(self):
    #    items = self.image_model.find_items('*')
    #    all_matrices = []
       
    #    for item in items:
    #        if hasattr(item, "np_image"):
    #            if item.np_image != None:
    #                all_matrices.append(item.np_image)
       
    #    print(f'{len(all_matrices)}')










#---------------------------------------------------
#FENÊTRE KNN
#---------------------------------------------------








































































class KlustRDatasetItem(QStandardItem):
    def __init__(self, id, name, translated='', rotated='', scaled='', label_count='', training_image_count='', test_image_count=''):
        super().__init__(name)

        self._id = id
        self._name = name

        if id == -1:
            pass
        else:
            for name, count in [['Training', training_image_count], ['Test', test_image_count]]:
                self.append_row([   
                        QStandardItem(name), 
                        QStandardItem(translated), 
                        QStandardItem(rotated), 
                        QStandardItem(scaled), 
                        QStandardItem(label_count), 
                        QStandardItem(count)])

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
    

    

class klustRDataset(QWidget):
    training_data_ready = Signal(dict)
    def __init__(self, klustr_dao ,parent=None):
        super().__init__(parent)
        self.dataset_model = QStandardItemModel()
        #self.set_model(self.dataset_model)
        self.klustr_dao = klustr_dao

    @Slot()
    def setupUi(self, klustrDataWidget):
        main_layout = QVBoxLayout(self)

        self.grbDataset = QGroupBox("Dataset")
        self.layout_dataset = QVBoxLayout(self.grbDataset)

        self.cmb_dataset = QComboBox()
        self.cmb_dataset.set_model(self.dataset_model)
        self.update_datasets(self.klustr_dao)
        self.cmb_dataset.currentIndexChanged.connect(self.on_dataset_changed)
        self.layout_dataset.add_widget(self.cmb_dataset)

        container_widget = QWidget()
        self.layout_datasetText = QHBoxLayout(container_widget)
        self.layout_dataset.add_widget(container_widget)

        self.grbIncluded = QGroupBox()
        self.grbIncluded.title = "Inclut dans Dataset"
        layout_included = QVBoxLayout(self.grbIncluded)

        self.label_category = QLabel("Category count:")
        self.label_category_count = QLabel("0")
        self.label_training = QLabel("Training image count:")
        self.label_training_count = QLabel("0")
        self.label_test = QLabel("Test image count:")
        self.label_test_count = QLabel("0")
        self.label_total_image = QLabel("Total image count:")
        self.label_total_count = QLabel("0")

        category_layout = QHBoxLayout()
        category_layout.add_widget(self.label_category)
        category_layout.add_widget(self.label_category_count)
        category_layout.add_stretch()

        training_layout = QHBoxLayout()
        training_layout.add_widget(self.label_training)
        training_layout.add_widget(self.label_training_count)
        training_layout.add_stretch()

        test_layout = QHBoxLayout()
        test_layout.add_widget(self.label_test)
        test_layout.add_widget(self.label_test_count)
        test_layout.add_stretch()

        total_layout = QHBoxLayout()
        total_layout.add_widget(self.label_total_image)
        total_layout.add_widget(self.label_total_count)
        total_layout.add_stretch()

        layout_included.add_layout(category_layout)
        layout_included.add_layout(training_layout)
        layout_included.add_layout(test_layout)
        layout_included.add_layout(total_layout)

        self.layout_datasetText.add_widget(self.grbIncluded)

        self.grbTransformation = QGroupBox()
        self.grbTransformation.title = "Transformation"
        layout_transformation = QVBoxLayout(self.grbTransformation)

        self.label_translated = QLabel("Translated:")
        self.label_translated_value = QLabel("false")
        self.label_rotated = QLabel("Rotated:")
        self.label_rotated_value = QLabel("false")
        self.label_scaled = QLabel("Scaled:")
        self.label_scaled_value = QLabel("false")

        translate_layout = QHBoxLayout()
        translate_layout.add_widget(self.label_translated)
        translate_layout.add_widget(self.label_translated_value)
        translate_layout.add_stretch()

        rotated_layout = QHBoxLayout()
        rotated_layout.add_widget(self.label_rotated)
        rotated_layout.add_widget(self.label_rotated_value)
        rotated_layout.add_stretch()

        scaled_layout = QHBoxLayout()
        scaled_layout.add_widget(self.label_scaled)
        scaled_layout.add_widget(self.label_scaled_value)
        scaled_layout.add_stretch()



        layout_transformation.add_layout(translate_layout)
        layout_transformation.add_layout(rotated_layout)
        layout_transformation.add_layout(scaled_layout)


        self.layout_datasetText.add_widget(self.grbTransformation)

        main_layout.add_widget(self.grbDataset)

        self.retranslateUi(klustrDataWidget)

    @Slot()
    def on_dataset_changed(self):
        """Appelé quand le dataset change - met à jour les stats ET calcule les données 3D"""
        self.update_dataset_stats_simple()
        self.compute_and_display_training_data()


    @Slot()
    def compute_and_display_training_data(self):
        """Calcule les vecteurs 3D de toutes les images d'entraînement du dataset sélectionné"""
        
        selected_item = self.get_selected_dataset_item()
        
        if selected_item is None:
            print("Aucun dataset sélectionné")
            return
        
        dataset_name = selected_item.name
        
        # Récupérer tous les labels du dataset
        labels = self.klustr_dao.labels_from_dataset(dataset_name)
        
        # Préparer les données par label
        training_image_par_label = {}
        total_images = 0
        
        for label in labels:
            label_id = label[0]
            label_name = label[1]
            
            # Récupérer les images d'ENTRAÎNEMENT pour ce label
            training_images = self.klustr_dao.image_from_dataset_label(dataset_name, label_id, True)
            
            training_image_par_label[label_name] = []
            
            for image_info in training_images:
                img_bytes = image_info[6]
                
                if img_bytes is None:
                    continue
                
                try:
                    qimage = QtNpConvert.qimage_from_png(img_bytes)
                    
                    if qimage.is_null():
                        continue
                    
                    image_array = QtNpConvert.np_from_qimage(qimage)
                    
                    # Calculer le vecteur 3D avec VOS méthodes
                    vecteur_3d = self.calculate_3d_descriptor(image_array)
                    
                    training_image_par_label[label_name].append(vecteur_3d)
                    total_images += 1
                
                except Exception as e:
                    print(f"Erreur lors du calcul du descripteur : {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        # Émettre le signal avec les données calculées
        print(f"Calcul terminé : {total_images} images traitées")
        for label, vectors in training_image_par_label.items():
            print(f"   - {label}: {len(vectors)} images")
        
        self.training_data_ready.emit(training_image_par_label)

    def calculate_3d_descriptor(self, image_array):
        """
        Calcule le vecteur 3D en utilisant VOS 3 axes :
        - Axe 1 : Indice de complexité (périmètre)
        - Axe 2 : Pourcentage de remplissage
        - Axe 3 : Nombre de transitions
        """
        # try:
            # Axe 1 : Indice de complexité
        axe1 = Axe1.calcul_indice_complexite(image_array)
        
        # Axe 2 : Analyse du remplissage
        centroid, farthest, percentage, distance = Axe2.analyze_image(image_array)
        axe2 = percentage
        
        # Axe 3 : Transitions sur un cercle
        axe3 = Axe3.count_nb_transitions_along__negative_circle(
            image_array, 
            center=(int(centroid[1]), int(centroid[0])),  # Centroid calculé
            thickness=10
        )
        
        return [axe1, axe2, axe3]
            
        # except Exception as e:
        #     print(f"Erreur calcul descripteur : {e}")
        #     import traceback
        #     traceback.print_exc()
        #     return [0, 0, 0]

    def get_training_images_from_dataset(self):
        """Retourne toutes les images d'ENTRAÎNEMENT du dataset sélectionné"""
        
        selected_item = self.get_selected_dataset_item()
        if selected_item is None:
            return []
        
        dataset_name = selected_item.name
        all_training_images = []
        
        # Récupérer les labels du dataset
        labels = self.klustr_dao.labels_from_dataset(dataset_name)
        
        for label in labels:
            label_id = label[0]
            label_name = label[1]
            
            # Récupérer UNIQUEMENT les images d'ENTRAÎNEMENT (training=True)
            training_images = self.klustr_dao.image_from_dataset_label(dataset_name, label_id, True)
            
            for image_info in training_images:
                all_training_images.append((image_info, label_name))
        
        return all_training_images

    @Slot()
    def retranslateUi(self, klustrDataWidget):
        klustrDataWidget.set_window_role = "klustrDataWidget"
        self.grbDataset.title = "Dataset"
        self.grbIncluded.title = "Inclut dans Dataset"
        self.label_category.text = "Category count:"
        self.label_training.text = "Training image count:"
        self.label_test.text = "Test image count:"
        self.label_total_image.text ="Total image count:"
        self.label_category_count.text ="0"
        self.label_training_count.text ="0"
        self.label_test_count.text ="0"
        self.label_total_count.text ="0"
        self.grbTransformation.title = "Transformation"
        self.label_translated.text ="Translated:"
        self.label_rotated.text ="Rotated:"
        self.label_scaled.text ="Scaled:"
        self.label_translated_value.text ="false"
        self.label_rotated_value.text ="false"
        self.label_scaled_value.text ="false"

        self.update_dataset_stats_simple()


    

    @Slot()
    def update_datasets(self, klustr_dao):
        self.dataset_model.clear()
        
        # Ajouter "Tous les datasets"
        #item = KlustRDatasetItem(-1, 'Toutes les images')
        #self.dataset_model.append_row(item)
        
        # Ajouter les datasets
        for dataset in klustr_dao.available_datasets:
            item = KlustRDatasetItem(
                dataset[0],  # id
                dataset[1],  # name
                'true' if dataset[2] else 'false',  # translated
                'true' if dataset[3] else 'false',  # rotated
                'true' if dataset[4] else 'false',  # scaled
                f'{dataset[5]}',  # label_count
                f'{dataset[6]}',  # training_image_count
                f'{dataset[7]}'   # test_image_count
            )
            self.dataset_model.append_row(item)
    
    def get_selected_dataset_id(self):
        """Retourne l'ID du dataset sélectionné"""
        item = self.dataset_model.item(self.current_index)
        if isinstance(item, KlustRDatasetItem):
            return item.id
        return None
    

    def get_selected_dataset_item(self):
        """Retourne l'item complet du dataset sélectionné"""
        current_index = self.cmb_dataset.current_index
        item = self.dataset_model.item(current_index)
        if isinstance(item, KlustRDatasetItem):
            return item
        return None
    

    @Slot()
    def update_dataset_stats_simple(self):
        #Version simplifiée utilisant directement les données du DAO
        selected_item = self.get_selected_dataset_item()
        if hasattr(self, '_updating_stats') and self._updating_stats:
            return
        
        self._updating_stats = True
        try:
            selected_item = self.get_selected_dataset_item()

            if selected_item is None:
                return

            
                # Récupérer les informations du dataset directement
            for dataset in self.klustr_dao.available_datasets:
                if dataset[0] == selected_item.id:
                    # dataset[0] = id
                    # dataset[2] = translated
                    # dataset[3] = rotated
                    # dataset[4] = scaled
                    # dataset[5] = label_count
                    # dataset[6] = training_image_count
                    # dataset[7] = test_image_count
                    # dataset[8] = total_image_count
                    self.label_category_count.text = str(dataset[5])
                    self.label_training_count.text = str(dataset[6])
                    self.label_test_count.text = str(dataset[7])
                    self.label_total_count.text = str(dataset[8])
                    self.label_translated_value.text = "true" if dataset[2] else "false"
                    self.label_rotated_value.text = "true" if dataset[3] else "false"
                    self.label_scaled_value.text = "true" if dataset[4] else "false"
                    break
        finally:
            self._updating_stats = False

        


class klustRParameter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot()
    def setupUi(self, klustrDataWidget):
        main_layout = QVBoxLayout(self)

        self.grb_parametre = QGroupBox("Paramètres Knn")
        self.layout_parametre = QVBoxLayout(self.grb_parametre)

        self.scoll_bar_k = QScrollBar()
        self.scoll_bar_k.minimum = (1)
        self.scoll_bar_k.maximum = (10)
        self.scoll_bar_k.value = 3
        self.scoll_bar_k.orientation = (Qt.Orientation.Horizontal)
        self.scoll_bar_k.valueChanged.connect(self.update_k_value)
        self.layout_parametre.add_widget(self.scoll_bar_k)

        self.scroll_bar_dist = QScrollBar()
        self.scroll_bar_dist.minimum = (1)
        self.scroll_bar_dist.maximum = (10)
        self.scroll_bar_dist.value = 5
        self.scroll_bar_dist.orientation = (Qt.Orientation.Horizontal)
        self.scroll_bar_dist.valueChanged.connect(self.update_dist_max_value)
        self.layout_parametre.add_widget(self.scroll_bar_dist)

        layout_k = QHBoxLayout()
        self.label_k = QLabel()
        self.label_k_value = QLabel()
        layout_k.add_widget(self.label_k)
        layout_k.add_widget(self.label_k_value)
        layout_k.add_stretch()

        layout_dist = QHBoxLayout()
        self.label_dist_max = QLabel()
        self.label_dist_max_value = QLabel()
        layout_dist.add_widget(self.label_dist_max)
        layout_dist.add_widget(self.label_dist_max_value)
        layout_dist.add_stretch()
        
        layout_k_dist = QHBoxLayout()
        layout_k_dist.add_layout(layout_k)
        layout_k_dist.add_layout(layout_dist)
        layout_k_dist.add_stretch()
        self.layout_parametre.add_layout(layout_k_dist)


        self.btn_about = QPushButton()
        self.btn_about.clicked.connect(self.about_klustrWidget)
        self.layout_parametre.add_widget(self.btn_about)

        

        main_layout.add_widget(self.grb_parametre)
        self.retranslateUi(klustrDataWidget)



    @Slot()
    def retranslateUi(self, klustrDataWidget):
        klustrDataWidget.set_window_role = "klustrDataWidget"
        self.grb_parametre.title = "Paramètres Knn"
        self.label_k.text ="K ="
        self.label_dist_max.text ="Max dist ="
        self.label_dist_max_value.text ="0.00"
        self.label_k_value.text ="0"
        self.btn_about.text ="A propos"

    @Slot()
    def update_k_value(self):
        k_value = self.scoll_bar_k.value
        self.label_k_value.text = str(k_value)

    @Slot()
    def update_dist_max_value(self):
        dist_value = self.scroll_bar_dist.value / 10.0
        self.label_dist_max_value.text = f"{dist_value:.2f}"


    def get_k_value(self):
        #Retourne la valeur actuelle de K
        return self.scoll_bar_k.value
    
    def get_dist_max_value(self):
        #Retourne la valeur actuelle de la distance max
        return self.scroll_bar_dist.value / 10.0
    
    @Slot()
    def about_klustrWidget(self):
        
        msgBox = QMessageBox()
        msgBox.text = ("Ce logiciel est le projet no 1 du cours C52.\n\n"
        
        "Il a été réalisé par :\n"
        "\t• Antoine Dextraze\n"
        "\t• Alexiane Chartrand\n"
        "\t• Laurentiu Dilion\n"
        "\t• Irvan Nayaradou\n"
        "\t• François Rajotte\n\n"
        
        "Il consiste à faire la classification KNN d'images avec 3 dimensions "
        "basées sur les concepts suivants :\n"
        "\t• L'indice de complexité\n"
        "\t• Le pourcentage de remplissage\n"
        "\t• Le nombre de transitions\n\n"
        "----------------------------------------------\n\n"

        "Nos 3 métriques pour nos formes:\n\n"

        "1. Indice de complexité (1er axe)\n"
        "\t• Valeur entre 0 et 1 (sans unité)\n"
        "\t• Mesure la complexité du contour d'une forme\n"
        "\t• Formule : 1 - (4π × Aire) / Périmètre²\n"
        "\t• Un cercle parfait donne ~0, une forme complexe donne ~1\n\n"

        "2. Pourcentage de remplissage (2e axe)\n"
        "\t• Valeur entre 0 et 1 (pourcentage normalisé)\n"
        "\t• Mesure la compacité de la forme\n"
        "\t• Calcule le rapport entre l'aire occupée et un cercle\n"
        "\t  englobant le tracé depuis le centroïde\n\n"

        "3. Nombre de transitions (Axe 3)\n"
        "\t• Valeur normalisée (sans unité)\n"
        "\t• Domaine : analyse de texture\n"
        "\t• Compte les transitions noir-blanc sur un cercle\n"
        "\t  imaginaire autour du centroïde\n"
        "\t• Permet de distinguer les formes pleines des formes\n"
        "\t  avec des découpes ou trous\n\n"

        "----------------------------------------------\n\n"

        




        )
        msgBox.exec()




class klustRSingleTest(QWidget):
    def __init__(self, klustr_dao,klustr_dataset_widget=None , parent=None):
        
        super().__init__(parent)
        self.klustr_dao = klustr_dao
        self.klustr_dataset_widget = klustr_dataset_widget


    @Slot()
    def setupUi(self, klustrDataWidget):
        main_layout = QVBoxLayout(self)

        self.grb_simple_test = QGroupBox("Test simple")
        self.layout_simple_test = QVBoxLayout(self.grb_simple_test)
        self.image_combobox_model = QStandardItemModel()
        self.cmb_image = QComboBox()
        self.cmb_image.set_model(self.image_combobox_model)
        self.cmb_image.currentIndexChanged.connect(self.update_image_display)
        self.layout_simple_test.add_widget(self.cmb_image)


        container_widget = QWidget()
        self.view_label_image = QLabel(container_widget)
        self.view_label_image.set_fixed_height(150)
        self.view_label_image.style_sheet = (u"background-color : #313D4A; padding : 10px 10px 10px 10px;")
        self.view_label_image.alignment = Qt.AlignCenter
        self.view_label_image.scaled_contents = False
        self.layout_simple_test.add_widget(self.view_label_image)



        self.btn_classify = QPushButton()
        #self.btn_classify.clicked.connect(self.classify_current_image)
        self.layout_simple_test.add_widget(self.btn_classify)

        self.label_classified = QLabel()
        self.label_classified.alignment = (Qt.AlignmentFlag.AlignCenter)
        self.layout_simple_test.add_widget(self.label_classified)
        
        main_layout.add_widget(self.grb_simple_test)

        self.retranslateUi(klustrDataWidget)
        self.update_images_from_dataset()
        


    

    @Slot()
    def update_images_from_dataset(self):
        """Charge toutes les images du dataset sélectionné dans cmb_image"""


        if not hasattr(self, 'image_combobox_model'):
            return

        if not hasattr(self, 'cmb_image'):
            return

        if self.klustr_dataset_widget is None:
            return

        try:
           #Pour temporairement modifier le cmb_image
           self.cmb_image.currentIndexChanged.disconnect(self.update_image_display)
        except:
           pass  # Ignorer si déjà déconnecté
       
        # Créer un nouveau modèle propre
        self.image_combobox_model = QStandardItemModel()
        self.cmb_image.set_model(self.image_combobox_model)

        selected_item = self.klustr_dataset_widget.get_selected_dataset_item()

        if selected_item is None:
            return
        
        
        # Créer un nouveau modèle propre
        self.image_combobox_model = QStandardItemModel()
        self.cmb_image.set_model(self.image_combobox_model)

        
        # Dataset spécifique sélectionné
        dataset_name = selected_item.name
        # Récupérer les labels du dataset
        labels = self.klustr_dao.labels_from_dataset(dataset_name)
        for label in labels:
            label_id = label[0]
            label_name = label[1]

            # Récupérer UNIQUEMENT les images de TEST (training=False)
            test_images = self.klustr_dao.image_from_dataset_label(dataset_name, label_id, False)
            for image_info in test_images:
                image_name = f"{label_name} - Test - {image_info[3]}"
                item = QStandardItem(image_name)
                item.set_data(image_info, Qt.UserRole) 
                self.image_combobox_model.append_row(item)

        self.cmb_image.currentIndexChanged.connect(self.update_image_display)

        if self.image_combobox_model.row_count() > 0:
            self.cmb_image.current_index = 0
            self.update_image_display()


    def get_training_images_from_dataset(self):
        """Retourne toutes les images d'ENTRAÎNEMENT du dataset sélectionné"""

        if self.klustr_dataset_widget is None:
            return []

        selected_item = self.klustr_dataset_widget.get_selected_dataset_item()
        if selected_item is None:
            return []

        dataset_name = selected_item.name
        all_training_images = []

        # Récupérer les labels du dataset
        labels = self.klustr_dao.labels_from_dataset(dataset_name)

        for label in labels:
            label_id = label[0]
            label_name = label[1]

            # Récupérer UNIQUEMENT les images d'ENTRAÎNEMENT (training=True)
            training_images = self.klustr_dao.image_from_dataset_label(dataset_name, label_id, True)

            for image_info in training_images:
                all_training_images.append((image_info, label_name))

        return all_training_images

    @Slot()
    def update_image_display(self):
        """Affiche l'image sélectionnée dans view_label_image, centrée"""
        
        if not hasattr(self, 'cmb_image') or not hasattr(self, 'image_combobox_model'):
            return
        
        current_index = self.cmb_image.current_index
        
        if current_index < 0:
            self.view_label_image.clear()
            self.view_label_image.text = ""
            return
        
        # Récupérer l'item sélectionné
        item = self.image_combobox_model.item(current_index)
        
        if item is None:
            return
        
        # Récupérer les données de l'image stockées dans l'item
        image_info = item.data(Qt.UserRole)
        
        if image_info is None:
            return
        
        # image_info[6] contient l'image complète (PNG)
        img = QtNpConvert.qimage_from_png(image_info[6])
        
        if not img.is_null():
            pixmap = QPixmap.from_image(img)
            
            label_size = self.view_label_image.size
            
            scaled_pixmap = pixmap.scaled(
                label_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.view_label_image.pixmap = scaled_pixmap
            
            self.view_label_image.text = ""
            
        else:
            # Si l'image est nulle, afficher un message
            self.view_label_image.clear()
            self.view_label_image.text = "Image non disponible"

    
    # fabrication du UI
    @Slot()
    def retranslateUi(self, klustrDataWidget):
        klustrDataWidget.set_window_role = "klustrDataWidget"
        self.grb_simple_test.title = "Teste simple"
        self.view_label_image.text =("")
        self.btn_classify.text ="Classifier"
        self.label_classified.text ="non-classifié"

    

    def get_current_image_info(self):
        #Retourne les informations de l'image actuellement sélectionnée

        if not hasattr(self, 'cmb_image') or not hasattr(self, 'image_combobox_model'):
            return None

        current_index = self.cmb_image.current_index

        if current_index < 0:
            return None

        item = self.image_combobox_model.item(current_index)

        if item is None:
            return None

        return item.data(Qt.UserRole)
    
    def get_current_image_as_array(self):
        #Retourne l'image actuelle sous forme de numpy array (150, 150)

        image_info = self.get_current_image_info()
        
        if image_info is None:
            return None
        
        
        qimage = QtNpConvert.qimage_from_png(image_info[6])
        print(image_info[6])
        if qimage.is_null():
            return None
        
        
        image_array = QtNpConvert.np_from_qimage(qimage)
        
        return image_array


    @Slot()
    def classify_current_image(self, k=None, dist_max=None):
        
        all_training_images = self.get_training_images_from_dataset()
    
        if not all_training_images:
            print("Aucune image d'entraînement trouvée dans le dataset.")
            self.label_classified.text = "Pas de données d'entraînement"
            return None
        
        # Préparer les images d'entraînement pour le KNN
        all_images_preparer = []
        
        for image_info, label_name in all_training_images:
            img_bytes = image_info[6]  # L'image complète
            
            if img_bytes is None:
                continue
             
            try:
                qimage = QtNpConvert.qimage_from_png(img_bytes)
                
                if qimage.is_null():
                    continue
                 
                image_array = QtNpConvert.np_from_qimage(qimage)
                vecteur_3d = self.calculate_3d_descriptor(image_array)


                all_images_preparer.append((vecteur_3d, label_name))
            
            except Exception as e:
                print(f"Erreur lors du décodage d'une image d'entraînement : {e}")
                continue
             
        if not all_images_preparer:
            print("Aucune image d'entraînement valide décodée.")
            self.label_classified.text = "Erreur de préparation"
            return None
        
        # Récupérer l'image de TEST sélectionnée dans cmb_test
        image_a_classifier = self.get_current_image_as_array()
        
        if image_a_classifier is None:
            self.label_classified.text = "Aucune image de test sélectionnée"
            return None

        
        # Récupérer les paramètres
        if k is None:
            k = 3
        if dist_max is None:
            dist_max = 0.5

        self.knn = KNNNumpy(k,dist_max, all_images_preparer,image_a_classifier)
        self.axe1 = Axe1.calcul_indice_complexite(image_a_classifier)
        centroid, farthest, percentage, distance = Axe2.analyze_image(image_a_classifier)
        self.axe2 = percentage

        self.axe3 = Axe3.count_nb_transitions_along__negative_circle(
            image_a_classifier, 
            center=(int(centroid[1]), int(centroid[0])),  # Le centroid calculé
            thickness=3
        )
        self.vecteur_3d_image_simple = np.array([self.axe1, self.axe2, self.axe3])


        predicted_label, avg_distance, confiance = self.knn.predict_image_actuelle(self.vecteur_3d_image_simple)

        if predicted_label is None:
            self.label_classified.text = f"Non classifié (distance trop grande: {avg_distance:.4f})"
            print(f"Classification rejetée - distance: {avg_distance:.4f} > {dist_max}")
        else:
            self.label_classified.text = f"Classé comme: {predicted_label}\n" \
                                          f"Distance moy: {avg_distance:.4f}\n" \
                                          f"Confiance: {confiance*100:.1f}%"
            print(f"Classification réussie:")
            print(f"Label prédit: {predicted_label}")
            print(f"Distance moyenne: {avg_distance:.4f}")
            print(f"Confiance: {confiance*100:.1f}%")

        #Retourner le vecteur 3D ET les résultats de classification
        return {
            'vecteur_3d': self.vecteur_3d_image_simple,
            'label': predicted_label,
            'distance': avg_distance,
            'confiance': confiance
        }
    

    def calculate_3d_descriptor(self, image_array):
    #Calcule le vecteur 3D (les 3 descripteurs) pour une image
        try:
            # Axe 1 : Indice de complexité
            axe1 = Axe1.calcul_indice_complexite(image_array)
            # Axe 2 : Analyse du remplissage
            centroid, farthest, percentage, distance = Axe2.analyze_image(image_array)
            axe2 = percentage
            # Axe 3 : Transitions sur un cercle
            axe3 = Axe3.count_nb_transitions_along__negative_circle(
                image_array, 
                center=(int(centroid[1]), int(centroid[0])),
                thickness=3
            )
            return [axe1, axe2, axe3]
        except Exception as e:
            print(f"Erreur calcul descripteur : {e}")
            return [0, 0, 0]



    
    

class KnnImageClassificationWidget(QWidget):
    """Widget pour la classification KNN avec visualisation 3D"""
    
    def __init__(self, klustr_dao, parent=None):
        super().__init__(parent)
        
        self.klustr_dao = klustr_dao
        
        # Créer le viewer 3D avec rotation automatique
        self.viewer_3d = Animation.QScatter3dViewer(auto_rotate=True)
        self.viewer_3d.title = "KNN Classification 3D"
        self.viewer_3d.axis_x.title = "Complexité"
        self.viewer_3d.axis_y.title = "Remplissage"
        self.viewer_3d.axis_z.title = "Transitions"
        
        # Créer le widget de contrôle (l'interface UI)
        self.control_widget = QWidget()
        # J'importe UiklustrDataWidget depuis ton fichier principal
        self.layout_control = QVBoxLayout(self.control_widget)


        
        self.uiDataset = klustRDataset(klustr_dao)
        self.uiSingleTest = klustRSingleTest(klustr_dao, self.uiDataset)
        self.uiParameter = klustRParameter()

        self.layout_control.add_widget(self.uiDataset)
        self.layout_control.add_widget(self.uiSingleTest)
        self.layout_control.add_widget(self.uiParameter)
        
        self.uiDataset.setupUi(self.control_widget)
        self.uiSingleTest.setupUi(self.control_widget)
        self.uiParameter.setupUi(self.control_widget)

        self.uiDataset.training_data_ready.connect(self.display_training_data_3d)

        self.uiDataset.cmb_dataset.currentIndexChanged.connect(
            self.uiSingleTest.update_images_from_dataset
        )
        

        self.uiSingleTest.btn_classify.clicked.connect(self.on_classify_clicked)

        
        # Layout horizontal : contrôles à gauche, viewer 3D à droite
        layout = QHBoxLayout(self)
        layout.add_widget(self.control_widget,1)
        layout.add_widget(self.viewer_3d , 2)
        layout.contents_margins = (QMargins(0, 0, 0, 0))
        

    @Slot(dict)
    def display_training_data_3d(self, training_data_by_label):
        """Affiche les données d'entraînement dans le viewer 3D"""
        if not training_data_by_label:
            print("Aucune donnée d'entraînement à afficher")
            return
        
        self.viewer_3d.clear()
        
        # Ajouter une série pour chaque label avec une couleur différente
        color_sequence = QColorSequence()
        
        for label_name, vectors_3d in training_data_by_label.items():
            if not vectors_3d:
                continue
            
            # Convertir en numpy array
            data_array = np.array(vectors_3d)
            
            # Obtenir une couleur unique pour ce label
            color = color_sequence.next()
            
            # Ajouter la série au viewer 3D
            self.viewer_3d.add_serie(data_array, color, f"Training - {label_name}")
            



    @Slot()
    def on_classify_clicked(self):
        k = self.uiParameter.get_k_value()
        dist_max = self.uiParameter.get_dist_max_value()
        
        # Appeler avec les valeurs
        test_vector_3d = self.uiSingleTest.classify_current_image(k, dist_max)
        if test_vector_3d is not None:
            print(f"Vecteur 3D du test : {test_vector_3d}")
            # Afficher le point de test en 3D avec une couleur spéciale
            self.add_test_point_3d(
                test_vector_3d['vecteur_3d'], 
                test_vector_3d['label'],
                test_vector_3d['confiance']
        )
        else:
            print("Aucun vecteur 3D retourné")
        

    @Slot()
    def add_test_point_3d(self, vector_3d, predicted_label=None, confiance=0):
        #Ajoute le point de test en 3D (en rouge vif)

        # S'assurer que c'est un numpy array 2D (1, 3)
        if isinstance(vector_3d, list):
            vector_3d = np.array(vector_3d)
        
        if vector_3d.ndim == 1:
            vector_3d = vector_3d.reshape(1, -1)
        
        test_data = vector_3d
        test_color = QColor(255, 0, 0)  # Rouge vif pour le point de test

        if predicted_label:
            title = f"Test: {predicted_label} ({confiance*100:.0f}%)"
        else:
            title = "Image à classifier (non classée)"

        
        self.viewer_3d.add_serie(test_data, test_color, title)
        print(f"Point de test ajouté en 3D : {test_data[0]}")



def main():
    app = QApplication(sys.argv)

    #A changer selon votre configuration d'ordinateur
    #credential = PostgreSQLCredential(password='Yoshi9603')
    credential = PostgreSQLCredential(password='AAAaaa123')
    # credential = PostgreSQLCredential(password='123')


    klustr_dao = PostgreSQLKlustRDAO(credential)

    # Créer le QTabWidget principal
    tab_widget = QTabWidget()
    tab_widget.window_title = "KlustR KNN Classifier"
    
    # Première vue : KlustR Source Viewer
    source_data_widget = KlustRDataSourceViewWidget(klustr_dao)
    
    # Deuxième vue : KNN Classification 3D
    knn_widget = KnnImageClassificationWidget(klustr_dao)
    
    # Ajouter les onglets
    tab_widget.add_tab(source_data_widget, "KlustR Source Viewer")
    tab_widget.add_tab(knn_widget, "Knn Image Classification")
    
    # Afficher la fenêtre principale
    tab_widget.resize(1200, 800)
    tab_widget.show()
    source_data_widget.show()

    #knn_widget.ui.cmb_dataset.add_items([f"{ds[1]} [{ds[5]}][{ds[8]}]" for ds in klustr_dao.available_datasets])

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    
  