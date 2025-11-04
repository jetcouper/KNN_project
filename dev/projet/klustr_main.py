import sys
import klustr_3d as Animation
import numpy as np
# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QSize,QRect,QMetaObject,QCoreApplication
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import  (QApplication, QWidget, QListView, QTreeView,  
                                QGroupBox, QLabel, QCheckBox, QPlainTextEdit,
                                QGridLayout, QHBoxLayout, QVBoxLayout, QSplitter, QSizePolicy,
                                QMessageBox,QStackedWidget, QTabWidget,QComboBox,QPushButton,QScrollBar)
from PySide6.QtGui import  (QImage, QPixmap, QIcon, QPainter, QFont, QPen, QBrush, QColor, 
                            QStandardItemModel, QStandardItem,
                            QClipboard)

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

        super().__init__(self._thumbnail_icon, self._name)

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






































class KlustR3DDatasetComboBox(QComboBox):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.dataset_model = QStandardItemModel()
        self.set_model(self.dataset_model)

    def update_datasets(self, klustr_dao):
        self.dataset_model.clear()
        
        # Ajouter "Tous les datasets"
        item = KlustRDatasetItem(-1, 'Toutes les images')
        self.dataset_model.append_row(item)
        
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
        item = self.dataset_model.item(self.current_index)
        if isinstance(item, KlustRDatasetItem):
            return item
        return None






class Ui_klustr3DDataWidget(QWidget):
    def __init__(self, klustr_dao, parent=None):
        
        super().__init__(parent)

        self.klustr_dao = klustr_dao


    


    @Slot()
    def setupUi(self, klustrDataWidget):
        klustrDataWidget.resize(390, 628)
        self.grbDataset = QGroupBox(klustrDataWidget)
        self.grbDataset.geometry = (QRect(19, 9, 351, 191))

        

        self.cmb_dataset = KlustR3DDatasetComboBox(self.grbDataset)
        self.cmb_dataset.geometry = (QRect(20, 30, 321, 31))
        self.cmb_dataset.update_datasets(self.klustr_dao)
        self.cmb_dataset.currentIndexChanged.connect(self.update_dataset_stats_simple)

        self.grbIncluded = QGroupBox(self.grbDataset)
        self.grbIncluded.geometry = (QRect(20, 60, 191, 121))

        self.label_category = QLabel(self.grbIncluded)
        self.label_category.geometry = (QRect(10, 30, 91, 16))

        self.label_training = QLabel(self.grbIncluded)
        self.label_training.geometry = (QRect(10, 50, 121, 16))

        self.label_test = QLabel(self.grbIncluded)
        self.label_test.geometry = (QRect(10, 70, 101, 16))

        self.label_total_image = QLabel(self.grbIncluded)
        self.label_total_image.geometry = (QRect(10, 90, 111, 16))

        self.label_category_count = QLabel(self.grbIncluded)
        self.label_category_count.geometry = (QRect(150, 30, 30, 20))
        self.label_category_count.alignment = (Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.label_training_count = QLabel(self.grbIncluded)
        self.label_training_count.geometry = (QRect(150, 50, 30, 20))
        self.label_training_count.alignment = (Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.label_test_count = QLabel(self.grbIncluded)
        self.label_test_count.geometry = (QRect(150, 70, 30, 20))
        self.label_test_count.alignment = (Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.label_total_count = QLabel(self.grbIncluded)
        self.label_total_count.geometry = (QRect(150, 90, 35, 20))
        self.label_total_count.alignment = (Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.grbTransformation = QGroupBox(self.grbDataset)
        self.grbTransformation.geometry = (QRect(220, 60, 121, 121))

        self.label_translated = QLabel(self.grbTransformation)
        self.label_translated.geometry = (QRect(10, 30, 71, 16))

        self.label_rotated = QLabel(self.grbTransformation)
        self.label_rotated.geometry = (QRect(10, 50, 49, 16))

        self.label_scaled = QLabel(self.grbTransformation)
        self.label_scaled.geometry = (QRect(10, 70, 49, 16))

        self.label_translated_value = QLabel(self.grbTransformation)
        self.label_translated_value.geometry = (QRect(80, 30, 31, 20))

        self.label_rotated_value = QLabel(self.grbTransformation)
        self.label_rotated_value.geometry = (QRect(80, 50, 31, 16))

        self.label_scaled_value = QLabel(self.grbTransformation)
        self.label_scaled_value.geometry = (QRect(80, 70, 31, 16))

        self.grb_simple_test = QGroupBox(klustrDataWidget)
        self.grb_simple_test.geometry = (QRect(20, 200, 351, 271))

        self.image_combobox_model = QStandardItemModel()
        self.cmb_image = QComboBox(self.grb_simple_test)
        self.cmb_image.geometry = (QRect(20, 30, 311, 24))
        self.cmb_image.set_model(self.image_combobox_model)
        self.cmb_image.currentIndexChanged.connect(self.update_image_display)


        self.view_label_image = QLabel(self.grb_simple_test)
        self.view_label_image.geometry = (QRect(20, 60, 311, 141))
        self.view_label_image.style_sheet = (u"background-color : #313D4A; padding : 10px 10px 10px 10px;")
        self.view_label_image.alignment = Qt.AlignCenter
        self.view_label_image.scaled_contents = False

        self.btn_classify = QPushButton(self.grb_simple_test)
        self.btn_classify.geometry = (QRect(20, 210, 311, 24))
        self.btn_classify.clicked.connect(self.classify_current_image)

        self.label_classified = QLabel(self.grb_simple_test)
        self.label_classified.geometry = (QRect(130, 240, 111, 20))
        self.label_classified.alignment = (Qt.AlignmentFlag.AlignCenter)

        self.grb_parametre = QGroupBox(klustrDataWidget)
        self.grb_parametre.geometry = (QRect(20, 470, 351, 101))


        self.scoll_bar_k = QScrollBar(self.grb_parametre)
        self.scoll_bar_k.geometry = (QRect(120, 40, 221, 21))
        self.scoll_bar_k.minimum = (1)
        self.scoll_bar_k.maximum = (10)
        self.scoll_bar_k.value = 3
        self.scoll_bar_k.orientation = (Qt.Orientation.Horizontal)
        self.scoll_bar_k.valueChanged.connect(self.update_k_value)

        self.scroll_bar_dist = QScrollBar(self.grb_parametre)
        self.scroll_bar_dist.geometry = (QRect(120, 75, 221, 21))
        self.scroll_bar_dist.minimum = (1)
        self.scroll_bar_dist.maximum = (10)
        self.scroll_bar_dist.value = 5
        self.scroll_bar_dist.orientation = (Qt.Orientation.Horizontal)
        self.scroll_bar_dist.valueChanged.connect(self.update_dist_max_value)

        self.label_k = QLabel(self.grb_parametre)
        self.label_k.geometry = (QRect(10, 40, 49, 21))
        self.label_k.alignment = (Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.label_dist_max = QLabel(self.grb_parametre)
        self.label_dist_max.geometry = (QRect(10, 80, 61, 16))

        self.label_dist_max_value = QLabel(self.grb_parametre)
        self.label_dist_max_value.geometry = (QRect(70, 80, 31, 20))

        self.label_k_value = QLabel(self.grb_parametre)
        self.label_k_value.geometry = (QRect(70, 41, 31, 20))

        self.btn_about = QPushButton(klustrDataWidget)
        self.btn_about.geometry = (QRect(20, 580, 351, 24))
        self.btn_about.clicked.connect(self.about_klustrWidget)

        self.retranslateUi(klustrDataWidget)
        self.update_dataset_stats_simple()


    @Slot()
    def update_dataset_stats_simple(self):
        """Version simplifiée utilisant directement les données du DAO"""
        selected_item = self.cmb_dataset.get_selected_dataset_item()
        
        if selected_item is None:
            return
        
        if selected_item.id == -1:
            # "Toutes les images"
            total_stats = self.klustr_dao.total_label_image_count
            if total_stats:
                self.label_category_count.text = str(total_stats[0][0])
                self.label_total_count.text = str(total_stats[0][1])
                self.label_training_count.text = "-"
                self.label_test_count.text = "-"
                self.label_translated_value.text = "mixte"
                self.label_rotated_value.text = "mixte"
                self.label_scaled_value.text = "mixte"
        else:
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
        self.update_images_from_dataset()

    @Slot()
    def update_images_from_dataset(self):
        """Charge toutes les images du dataset sélectionné dans cmb_image"""

        if not hasattr(self, 'image_combobox_model'):
            return

        if not hasattr(self, 'cmb_image'):
            return

        # Bloquer les signaux pendant la mise à jour
        self.cmb_image.block_signals = True

        # Vider le modèle
        self.image_combobox_model.clear()

        selected_item = self.cmb_dataset.get_selected_dataset_item()

        if selected_item is None:
            self.cmb_image.block_signals = False
            return

        if selected_item.id == -1:
            # Toutes les images disponibles
            all_labels = self.klustr_dao.available_labels

            for label in all_labels:
                label_id = label[0]
                label_name = label[1]

                # Récupérer toutes les images pour ce label
                images = self.klustr_dao.image_from_label(label_id)

                for image_info in images:
                    image_name = f"{label_name} - {image_info[3]}"

                    item = QStandardItem(image_name)
                    item.set_data(image_info, Qt.UserRole) 

                    self.image_combobox_model.append_row(item)

        else:
            # Dataset spécifique sélectionné
            dataset_name = selected_item.name

            # Récupérer les labels du dataset
            labels = self.klustr_dao.labels_from_dataset(dataset_name)

            for label in labels:
                label_id = label[0]
                label_name = label[1]

                # Récupérer les images d'entraînement
                training_images = self.klustr_dao.image_from_dataset_label(dataset_name, label_id, True)
                for image_info in training_images:
                    image_name = f"{label_name} - Training - {image_info[3]}"

                    item = QStandardItem(image_name)
                    item.set_data(image_info, Qt.UserRole)

                    self.image_combobox_model.append_row(item)

                # Récupérer les images de test
                test_images = self.klustr_dao.image_from_dataset_label(dataset_name, label_id, False)
                for image_info in test_images:
                    image_name = f"{label_name} - Test - {image_info[3]}"

                    item = QStandardItem(image_name)
                    item.set_data(image_info, Qt.UserRole) 

                    self.image_combobox_model.append_row(item)

        # Débloquer les signaux
        self.cmb_image.block_signals = False

        # Sélectionner la première image si disponible
        if self.image_combobox_model.row_count() > 0:
            self.cmb_image.current_index = 0
            # Forcer l'affichage de la première image
            self.update_image_display()

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




    
    
    @Slot()
    def about_klustrWidget(self):
        msgBox = QMessageBox()
        msgBox.text = ("Ce logiciel est le projet no 1 du cours C52. \r\n Il a été réalisé par :\r\n \u0009 - __étudiant_1__\r\n \u0009- __étudiant_n__ \r\n \r\n "
        "Il consiste à faire __quelque_chose__ avec les concepts suivants :\r\n \u0009- __concept_1__\r\n \u0009- __concept_n__\r\n \r\n Nos 3 descripteurs de forme sont :\r\n"
        " - __decripteur_1__\r\n \u0009 - en __unité__ pour le domaine __domaine__\r\n \u0009- correspondant à __courte_description__\r\n - __decripteur_2__\r\n \u0009"
        " - en __unité__ pour le domaine __domaine__\r\n \u0009- correspondant à __courte_description__\r\n - __decripteur_3__\r\n \u0009- en __unité__ pour le domaine __domaine__"
        "\r\n \u0009- correspondant à __courte_description__\r\n \r\n Plus précisément, ce laboratoire permet de mettre en pratique les notions de :\r\n"
        "\u0009 - __notion_1__\r\n \u0009- __notion_n__\r\n \r\n Un effort d'abstraction a été fait pour ces points :\r\n \u0009- __point_1__\r\n \u0009- __point_n__"
        "\r\n \r\nFinalement, l’ensemble de données le plus complexe que nous avons été capable de résoudre est\r\n :\r\n - __nom_de_l_ensemble_de_données__")
        msgBox.exec()

        #QMetaObject.connect_slots_by_name = (klustrDataWidget)
    # fabrication du UI
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
        self.grb_simple_test.title = "Teste simple"
        self.view_label_image.text =("")
        self.btn_classify.text ="Classifier"
        self.label_classified.text ="non-classifié"
        self.grb_parametre.title = "Paramètres Knn"
        self.label_k.text ="K ="
        self.label_dist_max.text ="Max dist ="
        self.label_dist_max_value.text ="0.00"
        self.label_k_value.text ="0"
        self.btn_about.text ="A propos"
    # traduction par défaut

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
    def classify_current_image(self):
        """Classifie l'image actuelle avec KNN"""
        #image_array = self.get_current_image_as_array_simple()

        image_array= self.get_current_image_as_array()

        if image_array is None:
            self.label_classified.text = "Aucune image"
            return
        
        # Récupérer les paramètres
        k = self.get_k_value()
        dist_max = self.get_dist_max_value()
        
        print(f"Image shape: {image_array.shape}")
        print(f"Classification avec K={k} et distance_max={dist_max}")
        
        # Appeler votre algorithme KNN
        # predicted_label = your_knn_classifier.classify(image_array, k=k, dist_max=dist_max)
        
        # Pour tester, afficher des infos
        self.label_classified.text = f"Shape: {image_array.shape}"
        
        # Exemple avec votre KNN :
        # self.label_classified.text = predicted_label
    
    















    
    
    
    # EXEMPLE DE STRUCTURE COMPLÈTE POUR KNN
    
    
    # class KNNImageClassifier:
    #     """Exemple de structure pour votre classificateur KNN"""
        
    #     def __init__(self, training_images, training_labels):
    #         """
    #         Args:
    #             training_images: numpy array shape (n_samples, 22500)
    #             training_labels: numpy array shape (n_samples,)
    #         """
    #         self.training_images = training_images
    #         self.training_labels = training_labels
        
    #     def classify(self, test_image, k=3, dist_max=1.0):
    #         """
    #         Classifie une image de test
            
    #         Args:
    #             test_image: numpy array shape (22500,)
    #             k: nombre de voisins
    #             dist_max: distance maximale acceptable
            
    #         Returns:
    #             label prédit (str)
    #         """
    #         # Calculer les distances euclidiennes
    #         distances = np.linalg.norm(self.training_images - test_image, axis=1)
            
    #         # Trouver les k plus proches voisins
    #         k_nearest_indices = np.argsort(distances)[:k]
    #         k_nearest_distances = distances[k_nearest_indices]
            
    #         # Filtrer par distance max
    #         valid_indices = k_nearest_indices[k_nearest_distances <= dist_max]
            
    #         if len(valid_indices) == 0:
    #             return "Inconnu"
            
    #         # Vote majoritaire
    #         k_nearest_labels = self.training_labels[valid_indices]
    #         unique, counts = np.unique(k_nearest_labels, return_counts=True)
    #         predicted_label = unique[np.argmax(counts)]
            
    #         return predicted_label



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
    knn_widget = Animation.KnnImageClassificationWidget(klustr_dao)
    
    # Ajouter les onglets
    tab_widget.add_tab(source_data_widget, "KlustR Source Viewer")
    tab_widget.add_tab(knn_widget, "Knn Image Classification")
    
    # Afficher la fenêtre principale
    tab_widget.resize(1200, 800)
    tab_widget.show()
    #source_data_widget.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
    