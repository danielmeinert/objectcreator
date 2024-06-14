# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QSlider, QTableWidgetItem, \
    QRadioButton
from PyQt5 import uic, QtGui, QtCore
from PIL import Image, ImageGrab, ImageDraw
from PIL.ImageQt import ImageQt
from copy import copy
import io
import os.path
from os import getcwd
import numpy as np
from pkgutil import get_data


import auxiliaries as aux

import customwidgets as cwdg
import widgets as wdg
import widgetsGeneric

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal
from rctobject import objects as obj


class SettingsTab(widgetsGeneric.SettingsTabAll):
    def __init__(self, o, object_tab, sprites_tab, author, author_id):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/settingsLS.ui'), self)

        self.o = o
        self.object_tab = object_tab
        self.sprites_tab = sprites_tab
        self.main_window = object_tab.main_window

        self.tab_widget = self.findChild(QTabWidget, "tabWidget_settingsLS")
        self.tab_widget.currentChanged.connect(self.tabChanged)

        super().initializeWidgets()

        self.button_set_defaults = self.findChild(
            QPushButton, "pushButton_applyDefaultSettings")
        self.button_set_defaults.clicked.connect(self.setDefaults)

        # Subtype combobox
        self.subtype_box = self.findChild(
            QComboBox, "comboBox_subtype")

        self.subtype_box.currentIndexChanged.connect(self.subtypeChanged)
        # disactivate 3d sign and scrolling sign for now
        for i in [1, 2]:
            self.subtype_box.model().item(i).setEnabled(False)

        # Flags
        for flag in cts.Jlarge_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.stateChanged.connect(
                    lambda x, flag=checkbox.objectName(): self.flagChanged(x, flag))

        checkbox = self.findChild(QCheckBox, 'hasTertiaryColour')
        checkbox.stateChanged.connect(
            lambda x, flag=checkbox.objectName(): self.flagChanged(x, flag))

        # Spinboxes
        self.spinbox_price = self.findChild(
            QDoubleSpinBox, "doubleSpinBox_price")
        self.spinbox_removal_price = self.findChild(
            QDoubleSpinBox, "doubleSpinBox_removalPrice")
        self.spinbox_version = self.findChild(
            QDoubleSpinBox, "doubleSpinBox_version")

        self.spinbox_price.valueChanged.connect(
            lambda value, name='price': self.spinBoxChanged(value, name))
        self.spinbox_removal_price.valueChanged.connect(
            lambda value, name='removalPrice': self.spinBoxChanged(value, name))
        self.spinbox_version.valueChanged.connect(
            lambda value, name='version': self.spinBoxChanged(value, name))

        self.loadObjectSettings(author=author, author_id=author_id)

    def giveDummy(self):
        dummy_o = obj.newEmpty(obj.Type.SMALL)

        return dummy_o

    def subtypeChanged(self, value):
        value = self.subtype_box.currentIndex()

        pass

    def loadObjectSettings(self, author=None, author_id=None):

        self.subtype_box.setCurrentIndex(self.o.subtype.value)

        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(self.o['properties'].get(flag, False))

        checkbox = self.findChild(QCheckBox, 'hasTertiaryColour')
        checkbox.setChecked(self.o['properties'].get(
            'hasTertiaryColour', False))

        self.cursor_box.setCurrentIndex(cts.cursors.index(
            self.o['properties'].get('cursor', 'CURSOR_BLANK')))

        if not author:
            author = self.o.data.get('authors', '')
            if isinstance(author, list):
                author = ', '.join(author)

        self.author_field.setText(author)
        self.author_id_field.setText(author_id)

        obj_id = self.o.data.get('id', False)
        if obj_id:
            if len(obj_id.split('.')) > 2:
                self.author_id_field.setText(obj_id.split('.')[0])
                self.object_id_field.setText(obj_id.split('.', 2)[2])
            else:
                self.object_id_field.setText(obj_id)

        dat_id = self.o.data.get('originalId', False)
        if dat_id:
            self.object_original_id_field.setText(
                dat_id.split('|')[1].replace(' ', ''))

        self.object_name_field.setText(
            self.o['strings']['name'].get('en-GB', ''))
        self.object_name_lang_field.setText(
            self.o['strings']['name'].get('en-GB', ''))

        self.spinbox_price.setValue(self.o['properties'].get('price', 1))
        self.spinbox_removal_price.setValue(
            self.o['properties'].get('removalPrice', 1))
        self.spinbox_version.setValue(float(self.o.data.get('version', 1.0)))

        if self.main_window.settings.get('clear_languages', False):
            self.clearAllLanguages()

    def setDefaults(self):

        settings_LS = self.main_window.settings.get(
            'large_scenery_defaults', {})

        for flag in settings_LS:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(settings_LS.get(flag, False))

        self.spinbox_price.setValue(settings_LS.get('price', 1))
        self.spinbox_removal_price.setValue(settings_LS.get('removalPrice', 1))
        self.spinbox_version.setValue(settings_LS.get('version', 1.0))

        self.cursor_box.setCurrentIndex(cts.cursors.index(
            settings_LS.get('cursor', 'CURSOR_BLANK')))


class SpritesTab(QWidget):
    def __init__(self, o, object_tab):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/spritesLS.ui'), self)

        self.o = o
        self.object_tab = object_tab
        self.main_window = object_tab.main_window

        self.viewing_mode = 0  # projection

        # Buttons load/reset
        self.button_load_image = self.findChild(
            QPushButton, "pushButton_loadImage")

        self.button_load_image.clicked.connect(self.loadImage)

        self.button_cycle_rotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")

        self.button_cycle_rotation.clicked.connect(self.cycleRotation)

        self.sprite_view_main.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sprite_view_main.customContextMenuRequested.connect(
            self.showSpriteMenu)
        self.sprite_view_main.setBackgroundBrush(
            QtGui.QBrush(
                QtGui.QColor(
                    self.main_window.current_background_color[0],
                    self.main_window.current_background_color[1],
                    self.main_window.current_background_color[2])))

        self.sprite_view_main_item = QGraphicsPixmapItem()
        self.sprite_view_main_scene = QGraphicsScene()
        self.sprite_view_main_scene.addItem(self.sprite_view_main_item)
        self.sprite_view_main_scene.setSceneRect(0, 0, 261, 268)
        self.sprite_view_main.setScene(self.sprite_view_main_scene)

        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1,
                               self.sprite_view_preview2, self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent = (
                lambda e, rot=rot: self.previewClicked(rot))
            self.sprite_preview[rot].setStyleSheet(
                f"background-color :  rgb{self.main_window.current_background_color};")

        # Remap Color Buttons
        self.button_first_remap = self.findChild(
            QPushButton, 'pushButton_firstRemap')
        self.button_first_remap.colorChanged.connect(
            lambda color, remap="1st Remap": self.clickChangeRemap(color, remap=remap))
        self.button_first_remap.setColor(self.main_window.settings.get(
            'default_remaps', ['NoColor', 'NoColor', 'NoColor'])[0])

        self.button_second_remap = self.findChild(
            QPushButton, 'pushButton_secondRemap')
        self.button_second_remap.colorChanged.connect(
            lambda color, remap="2nd Remap": self.clickChangeRemap(color, remap=remap))
        self.button_second_remap.setColor(self.main_window.settings.get(
            'default_remaps', ['NoColor', 'NoColor', 'NoColor'])[1])

        self.button_third_remap = self.findChild(
            QPushButton, 'pushButton_thirdRemap')
        self.button_third_remap.colorChanged.connect(
            lambda color, remap="3rd Remap": self.clickChangeRemap(color, remap=remap))
        self.button_third_remap.setColor(self.main_window.settings.get(
            'default_remaps', ['NoColor', 'NoColor', 'NoColor'])[2])

        self.button_first_remap.panelOpened.connect(
            self.button_second_remap.hidePanel)
        self.button_first_remap.panelOpened.connect(
            self.button_third_remap.hidePanel)

        self.button_second_remap.panelOpened.connect(
            self.button_first_remap.hidePanel)
        self.button_second_remap.panelOpened.connect(
            self.button_third_remap.hidePanel)

        self.button_third_remap.panelOpened.connect(
            self.button_second_remap.hidePanel)
        self.button_third_remap.panelOpened.connect(
            self.button_first_remap.hidePanel)

        self.button_projection_mode = self.findChild(
            QRadioButton, "radioButton_projection")
        self.button_tiles_mode = self.findChild(
            QRadioButton, "radioButton_tiles")

        self.button_projection_mode.clicked.connect(
            lambda: self.changeViewMode('projection'))
        self.button_tiles_mode.clicked.connect(
            lambda: self.changeViewMode('tiles'))

        self.previewClicked(0)
        self.updateAllViews()

    def loadImage(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            sprite = spr.Sprite.fromFile(filepath, palette=self.main_window.current_palette,
                                         transparent_color=self.main_window.current_import_color)
            layer = wdg.SpriteLayer(sprite, self.main_window, 0, 0)

            layers = QtGui.QStandardItemModel()
            layers.insertRow(0, layer)

            self.setCurrentLayers(layers)

        self.updateLockedSpriteLayersModel()
        self.updateMainView()

    def showSpriteMenu(self, pos):
        menu = QMenu()
        menu.addAction("Paste Sprite", self.pasteSpriteFromClipboard)
        menu.addAction("Copy Sprite", self.copySpriteToClipboard)

        submenu_copy = QMenu("Copy Sprite to")
        rot = self.o.rotation
        submenu_copy.addAction(
            f"View {(rot + 1 )%4+1}", lambda view=(rot + 1) % 4: self.copySpriteToView(view))
        submenu_copy.addAction(
            f"View {(rot + 2 )%4+1}", lambda view=(rot + 2) % 4: self.copySpriteToView(view))
        submenu_copy.addAction(
            f"View {(rot + 3 )%4+1}", lambda view=(rot + 3) % 4: self.copySpriteToView(view))
        submenu_copy.addAction("All Views", self.copySpriteToAllViews)

        menu.addMenu(submenu_copy)

        menu.addAction("Delete Sprite", self.deleteSprite)

        menu.exec_(self.sprite_view_main.mapToGlobal(pos))

    def pasteSpriteFromClipboard(self):
        image = ImageGrab.grabclipboard()
        if type(image) == list:
            try:
                image = Image.open(image[0])
            except:
                return

        if image:
            image = image.convert('RGBA')

            sprite = spr.Sprite(image, palette=self.main_window.current_palette,
                                transparent_color=self.main_window.current_import_color)
            layer = wdg.SpriteLayer(sprite, self.main_window, 0, 0)

            layers = QtGui.QStandardItemModel()
            layers.insertRow(0, layer)

            self.setCurrentLayers(layers)

        self.updateLockedSpriteLayersModel()
        self.updateMainView()

    def copySpriteToClipboard(self):
        pixmap = self.sprite_view_main_item.pixmap()

        QApplication.clipboard().setPixmap(pixmap)

    def copySpriteToView(self, view):
        layers = QtGui.QStandardItemModel()

        for i, layer in enumerate(self.giveCurrentMainViewLayers()):
            layers.insertRow(i, wdg.SpriteLayer.fromLayer(layer))

        self.setCurrentLayers(layers, view=view)

        self.updateLockedSpriteLayersModel()
        self.updatePreview(view)

    def copySpriteToAllViews(self):
        rot = self.o.rotation

        for view in range(3):
            self.copySpriteToView(view=(view+rot + 1) % 4)

    def deleteSprite(self):
        for layer in self.giveCurrentMainViewLayers():
            layer.sprite.clearSprite()

        self.updateLockedSpriteLayersModel()
        self.updateMainView()

    def cycleRotation(self):
        self.o.cycleSpritesRotation()

        self.updateLockedSpriteLayersModel()
        self.updateAllViews()

    def previewClicked(self, rot):
        old_rot = self.o.rotation
        self.sprite_preview[old_rot].setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color}; border:2px outset rgb{self.main_window.current_background_color};")
        self.sprite_preview[rot].setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color}; border:2px outset green;")

        self.o.setRotation(rot)

        backbox, coords = self.main_window.bounding_boxes.giveBackbox(self.o)
        self.object_tab.boundingBoxChanged.emit(
            self.main_window.layer_widget.button_bounding_box.isChecked(), backbox, coords)
        symm_axis, coords = self.main_window.symm_axes.giveSymmAxes(self.o)
        self.object_tab.symmAxesChanged.emit(
            self.main_window.layer_widget.button_symm_axes.isChecked(), symm_axis, coords)
        self.object_tab.rotationChanged.emit(rot)

        self.updateMainView()

    def clickRemapButton(self, panel_index):
        for i, panel in enumerate(self.select_panels_remap):
            if i == panel_index:
                if panel.isVisible():
                    panel.hide()
                else:
                    panel.show()
            else:
                panel.hide()

    def clickChangeRemap(self, color, remap):
        self.o.changeRemap(color, remap)

        self.updateAllViews()

    def createLayers(self, base_x, base_y):
        self.layers = [[], [], [], []]

        if self.viewing_mode == 0:  # projection mode
            for rot in range(4):
                im, x, y = self.o.show(rotation=rot, no_remaps=True)
                sprite = spr.Sprite(
                    im, (x, y), palette=self.main_window.current_palette, already_palletized=True)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, base_x, base_y, name=f'View {rot+1}')
                self.layers[rot].append(layer)

    def updateLockedSpriteLayersModel(self):
        if self.object_tab.locked:
            self.createLayers(self.object_tab.locked_sprite_tab.base_x,
                              self.object_tab.locked_sprite_tab.base_y)
            self.object_tab.locked_sprite_tab.updateLayersModel()
            self.updateAllViews()

    def giveCurrentMainViewLayers(self):
        return self.layers[self.o.rotation]

    def requestNumberOfLayers(self):
        if self.o.subtype == self.o.Subtype.SIMPLE:
            return 1
        elif self.o.subtype == self.o.Subtype.ANIMATED:
            if self.o.animation_type == obj.SmallScenery.AnimationType.FOUNTAIN1:
                return 2
            elif self.o.animation_type == obj.SmallScenery.AnimationType.FOUNTAIN4:
                return 4
            else:
                return 1
        elif self.o.subtype == self.o.Subtype.GLASS:
            return 2
        elif self.o.subtype == self.o.Subtype.GARDENS:
            return 3

    def setCurrentLayers(self, layers, view=None):
        if view == None:
            view = self.o.rotation

        if self.requestNumberOfLayers() != layers.rowCount():
            dialog = SpriteImportUi(layers, self.layers[view])

            if dialog.exec():
                target_index = dialog.selected_index
                layers_incoming = dialog.selected_incoming

                if len(layers_incoming) == 0:
                    return

                layer_top = layers_incoming[0]
                for i in range(len(layers_incoming)-1):
                    layer_bottom = layers_incoming[i+1]
                    layer_bottom.merge(layer_top)
                    layer_top = layer_bottom

                target_layer = self.layers[view][target_index]
                target_layer.sprite.setFromSprite(layer_top.sprite)

            else:
                return
        else:
            for i in range(layers.rowCount()):
                index = layers.rowCount() - i - 1
                target_layer = self.layers[view][i]
                target_layer.sprite.setFromSprite(layers.item(
                    index, 0).sprite)

        if self.object_tab.locked:
            self.createLayers(self.object_tab.locked_sprite_tab.base_x,
                              self.object_tab.locked_sprite_tab.base_y)
            self.object_tab.locked_sprite_tab.updateLayersModel()

        self.updateMainView()

    def addSpriteToHistoryAllViews(self, index):
        for rot in range(4):
            self.layers[rot][index].addSpriteToHistory()

    def colorRemapToAll(self, index, color_remap, selected_colors):
        self.addSpriteToHistoryAllViews(index)

        for rot in range(4):
            sprite = self.layers[rot][index].sprite
            for color in selected_colors:
                sprite.remapColor(color, color_remap)

        self.updateAllViews()

    def colorChangeBrightnessAll(self, index, step, selected_colors):
        self.addSpriteToHistoryAllViews(index)

        for rot in range(4):
            sprite = self.layers[rot][index].sprite
            for color in selected_colors:
                sprite.changeBrightnessColor(step, color)

        self.updateAllViews()

    def colorRemoveAll(self, index, selected_colors):
        self.addSpriteToHistoryAllViews(index)

        for rot in range(4):
            sprite = self.layers[rot][index].sprite
            for color in selected_colors:
                sprite.removeColor(color)

        self.updateAllViews()

    def updateMainView(self, emit_signal=True):

        im, x, y = self.o.show()

        height = -y + 90 if -y > 178 else 268
        self.sprite_view_main_scene.setSceneRect(0, 0, 261, height)

        coords = (261//2+x, height-70+y)

        image = ImageQt(im)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main_item.setOffset(coords[0], coords[1])

        self.sprite_view_main_item.setPixmap(pixmap)

        self.updatePreview(self.o.rotation)
        if emit_signal:
            self.object_tab.mainViewUpdated.emit()

    def updatePreview(self, rot):
        im, x, y = self.o.show(rotation=rot)

        im = copy(im)
        im.thumbnail((72, 72), Image.NEAREST)
        coords = (int(34-im.size[0]/2), int(36-im.size[1]/2))

        canvas = Image.new('RGBA', (72, 72))
        canvas.paste(im, coords)
        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)

    def updateAllViews(self):
        self.updateMainView()
        for rot in range(4):
            self.updatePreview(rot)


class SpriteImportUi(QDialog):
    def __init__(self, layers_incoming, layers_object):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/sprite_import.ui'), self)

        self.setFixedSize(self.size())
        self.layers_incoming = layers_incoming
        self.layers_object = layers_object

        for i in range(layers_incoming.rowCount()):
            index = layers_incoming.rowCount() - i - 1
            layer = layers_incoming.item(index, 0)
            self.list_layers_incoming.insertItem(0, layer.text())

        for layer in layers_object:
            self.list_layers_object.insertItem(0, layer.text())

        self.list_layers_incoming.setCurrentRow(0)
        self.list_layers_object.setCurrentRow(0)

    def accept(self):

        self.selected_incoming = []

        for item in self.list_layers_incoming.selectedItems():
            index = self.list_layers_incoming.row(item)

            self.selected_incoming.append(self.layers_incoming.item(index, 0))

        self.selected_index = self.list_layers_object.count(
        ) - self.list_layers_object.currentRow() - 1

        super().accept()


class EditAnimationSequenceUI(QDialog):
    def __init__(self, o):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/animation_edit.ui'), self)

        self.o = o
        self.sequence = list(o['properties'].get('frameOffsets', [0]))
        self.num_image_sets = int(o.num_image_sets)

        self.table.setRowCount(len(self.sequence))
        self.spinbox_length.setValue(len(self.sequence))
        self.table.setColumnCount(self.num_image_sets)
        self.spinbox_num_sprites.setValue(self.num_image_sets)

        self.table.cellClicked.connect(self.cellClicked)
        self.spinbox_length.valueChanged.connect(self.lengthChanged)
        self.spinbox_num_sprites.valueChanged.connect(self.numSpritesChanged)

        self.button_ascending.clicked.connect(self.ascending)
        self.button_descending.clicked.connect(self.descending)
        self.button_back_forth.clicked.connect(self.backForth)

        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 10)

        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 10)

        self.resize(self.layout().sizeHint())
        self.updateTable()

    def cellClicked(self, row, column):
        self.sequence[row] = column

        self.updateTable()

    def lengthChanged(self, value):
        old_len = len(self.sequence)

        if old_len < value:
            for i in range(value-old_len):
                self.sequence.append(0)
        else:
            self.sequence = self.sequence[:value]

        self.table.setRowCount(value)
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 10)

        self.resize(self.layout().sizeHint())
        self.updateTable()

    def numSpritesChanged(self, value):
        old_len = max(self.sequence)

        if old_len > value-1:
            self.sequence = [value-1 if x ==
                             old_len else x for x in self.sequence]

        self.table.setColumnCount(value)
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 10)

        self.num_image_sets = value

        self.resize(self.layout().sizeHint())
        self.updateTable()

    def ascending(self):
        self.spinbox_num_sprites.setValue(self.table.rowCount())

        self.sequence = [i for i in range(self.table.rowCount())]

        self.updateTable()

    def descending(self):
        length = self.table.rowCount()
        self.spinbox_num_sprites.setValue(length)

        self.sequence = [length-i-1 for i in range(length)]

        self.updateTable()

    def backForth(self):
        length = int(self.table.rowCount()/2)
        if length < 2:
            return

        self.spinbox_num_sprites.setValue(length)

        self.sequence[:length] = [i for i in range(length)]
        self.sequence[length:] = [length-i-1 for i in range(length)]

        self.updateTable()

    def updateTable(self):
        self.table.clearContents()

        for row, column in enumerate(self.sequence):
            item = QTableWidgetItem()
            self.table.setItem(row, column, item)
            item.setBackground(QtCore.Qt.green)
