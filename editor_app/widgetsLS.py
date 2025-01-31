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
from enum import Enum


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
        super().__init__(o, object_tab, sprites_tab)
        uic.loadUi(aux.resource_path('gui/settingsLS.ui'), self)

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
        if self.sprites_tab.view_mode == self.sprites_tab.ViewMode.PROJECTION:
            dummy_o = obj.newEmpty(obj.Type.LARGE)
            size = self.o.size()
            dummy_o.changeShape(*size)
            dummy_o.setRotation(self.o.rotation)

            dummy_o['properties']['height'] = int(size[2]*8)

            offset_x, offset_y = self.o.baseOffset()
            offset_x -= self.o.centerOffset()[0]
            offset_y -= self.o.centerOffset()[1]

            return dummy_o, (offset_x, offset_y)

        elif self.sprites_tab.view_mode == self.sprites_tab.ViewMode.TILES:
            tile = self.o.tiles[self.sprites_tab.active_layer_id]
            dummy_o = obj.newEmpty(obj.Type.SMALL)
            dummy_o.changeShape(obj.SmallScenery.Shape.FULL)
            dummy_o['properties']['height'] = int(tile.h*8)

            offset_x, offset_y = self.o.baseOffset()
            offset_x -= self.o.centerOffset()[0]
            offset_y -= self.o.centerOffset()[1]

            return dummy_o, (32*(-tile.x + tile.y)+offset_x, 16*(tile.x+tile.y)-8*tile.z+offset_y)

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


class SpritesTab(widgetsGeneric.SpritesTabAll):
    def __init__(self, o, object_tab):
        super().__init__(o, object_tab)
        uic.loadUi(aux.resource_path('gui/spritesLS.ui'), self)

        self.view_mode = self.ViewMode.TILES

        self.initializeWidgets(261, 268)

        # Buttons projection mode
        self.button_projection_mode = self.findChild(
            QRadioButton, "radioButton_projection")
        self.button_tiles_mode = self.findChild(
            QRadioButton, "radioButton_tiles")

        self.button_projection_mode.clicked.connect(
            lambda: self.changeViewMode(self.ViewMode.PROJECTION))
        self.button_tiles_mode.clicked.connect(
            lambda: self.changeViewMode(self.ViewMode.TILES))

#        self.changeViewMode(self.ViewMode.PROJECTION)
        self.previewClicked(0)
        self.updateAllViews()

    def save(self):
        self.projectSprites()

        self.o.createThumbnails()

    def createProjectionSprites(self):
        self.projectionSprites = []

        for rot in range(4):
            im, x, y = self.o.show(rotation=rot, no_remaps=True)
            sprite = spr.Sprite(
                im, (x, y), palette=self.main_window.current_palette, already_palettized=True)
            self.projectionSprites.append(sprite)

    def projectSprites(self):
        for rot in range(4):
            sprite = self.projectionSprites[rot]

            self.o.projectSpriteToTiles(sprite, rot)

        self.updateAllViews()

    def changeViewMode(self, mode):
        self.view_mode = mode
        if mode == self.ViewMode.PROJECTION:
            self.createProjectionSprites()
        elif mode == self.ViewMode.TILES:
            self.projectSprites()

        self.updateLockedSpriteLayersModel()

    # override base class method
    def activeLayerChanged(self, layer):
        self.active_layer_id = layer.locked_id

        dummy_o, dummy_coords = self.object_tab.giveDummy()

        backbox, coords = self.main_window.bounding_boxes.giveBackbox(dummy_o)
        self.object_tab.boundingBoxChanged.emit(
            self.main_window.layer_widget.button_bounding_box.isChecked(), backbox, (coords[0]+dummy_coords[0], coords[1] + dummy_coords[1]))

    def createLayers(self):
        self.layers = [[], [], [], []]

        if self.view_mode == self.ViewMode.PROJECTION:
            for rot in range(4):
                sprite = self.projectionSprites[rot]
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, 0, 0, 0, 0, name=f'View {rot+1}')
                self.layers[rot].append(layer)
        elif self.view_mode == self.ViewMode.TILES:
            center_x, center_y = self.o.centerOffset()
            for rot in range(4):
                for tile_entry in self.o.getOrderedTileSprites(rot):
                    layer = wdg.SpriteLayer(
                        tile_entry[0], self.main_window, 0, 0, -center_x+tile_entry[1], -center_y+tile_entry[2], name=f'View {rot+1} Tile {tile_entry[3]+1}', locked_id=tile_entry[3])
                    self.layers[rot].append(layer)

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
            self.createLayers()
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

        if self.view_mode == self.ViewMode.PROJECTION:
            sprite = self.projectionSprites[self.o.rotation]
            im, x, y = sprite.show(
                self.o.current_first_remap, self.o.current_second_remap, self.o.current_third_remap), sprite.x, sprite.y
        else:
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
        if self.view_mode == self.ViewMode.PROJECTION:
            sprite = self.projectionSprites[rot]
            im, x, y = sprite.show(
                self.o.current_first_remap, self.o.current_second_remap, self.o.current_third_remap), sprite.x, sprite.y
        else:
            im, x, y = self.o.show(rotation=rot)

        im = copy(im)
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        im.thumbnail((72, 72), Image.NEAREST)
        coords = (int(34-im.size[0]/2), int(36-im.size[1]/2))

        canvas = Image.new('RGBA', (72, 72))
        canvas.paste(im, coords)
        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)

    class ViewMode(Enum):
        PROJECTION = 0, 'Projection'
        TILES = 1, 'Tiles'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value


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
