# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from operator import index
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QSlider, QTableWidgetItem, \
    QRadioButton, QHeaderView
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

        self.current_tile_index = 0


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

        # Tiles control
        self.spinbox_x = self.findChild(
            QSpinBox, "spinBox_size_x")
        self.spinbox_y = self.findChild(
            QSpinBox, "spinBox_size_y")

        #self.table.cellClicked.connect(self.cellClicked)
        self.table.currentCellChanged.connect(self.cellClicked)
        
        self.spinbox_x.valueChanged.connect(
            lambda value: self.sizeChanged(x=value))
        self.spinbox_y.valueChanged.connect(
            lambda value: self.sizeChanged(y=value))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().setDefaultSectionSize(25)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(25)
        
        self.button_add_tile = self.findChild(QPushButton, "pushButton_add_tile")
        self.button_remove_tile = self.findChild(
            QPushButton, "pushButton_remove_tile")
        self.button_add_tile.clicked.connect(self.addTile)
        self.button_remove_tile.clicked.connect(self.removeTile)
        self.button_fill_shape = self.findChild(QPushButton, "pushButton_fill_all")
        self.button_fill_shape.clicked.connect(self.fillShape)
        self.button_inner_borders = self.findChild(QPushButton, "pushButton_innerborders")
        self.button_inner_borders.clicked.connect(self.detectInnerBorders)

         # Tile settings
        
        self.checkbox_tile_sync = self.findChild(QCheckBox, "checkBox_synctiles")
        self.checkbox_tile_sync.stateChanged.connect(self.checkboxTileSyncChanged)
        
        self.spinbox_tile_z = self.findChild(QSpinBox, "spinBox_tile_z")
        self.spinbox_tile_h = self.findChild(QSpinBox, "spinBox_tile_h")

        self.spinbox_tile_z.valueChanged.connect(lambda x: self.tileSpinBoxChanged(x, 'z'))
        self.spinbox_tile_h.valueChanged.connect(lambda x: self.tileSpinBoxChanged(x, 'h'))

        self.checkbox_has_supports = self.findChild(QCheckBox, "checkBox_hassupports")
        self.checkbox_has_supports.stateChanged.connect(lambda x: self.tileFlagChanged(x, 'hasSupports'))
        self.checkbox_allow_supports = self.findChild(QCheckBox, "checkBox_allowsupports")
        self.checkbox_allow_supports.stateChanged.connect(lambda x: self.tileFlagChanged(x, 'allowSupports'))

        self.buttons_corners = [self.findChild(QPushButton, f"pushButton_q{i}") for i in range(4)]
        self.buttons_walls = [self.findChild(QPushButton, f"pushButton_w{i}") for i in range(4)]
        
        filter = cwdg.ButtonEventFilter(self)
        for i, button in enumerate(self.buttons_corners):
            button.toggled.connect(lambda val, index=i: self.toggleCorner(val, index))
            button.installEventFilter(filter)

        for i, button in enumerate(self.buttons_walls):
            button.toggled.connect(lambda val, index=i: self.toggleWall(val, index))
            button.installEventFilter(filter)

        self.loadObjectSettings(author=author, author_id=author_id)

    def giveCurrentTile(self):
        if self.current_tile_index is None:
            return None
        else:
            return self.o.tiles[self.current_tile_index]

    def giveDummy(self):
        if self.sprites_tab.view_mode == self.sprites_tab.ViewMode.PROJECTION:
            dummy_o = obj.newEmpty(obj.Type.LARGE)
            size = self.o.size()
            dummy_o.copyTilesGeometry(self.o.tiles)
            #dummy_o.setRotation(self.o.rotation)

            dummy_o['properties']['height'] = int(size[2]*8)

            offset_x, offset_y = self.o.baseOffset()
            offset_x -= self.o.centerOffset()[0]
            offset_y -= self.o.centerOffset()[1]

            return dummy_o, (offset_x, offset_y)

        elif self.sprites_tab.view_mode == self.sprites_tab.ViewMode.TILES:
            tile = self.giveCurrentTile()
            
            if tile is None:
                return None, (0, 0)
            
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

        size = self.o.size()
        self.spinbox_x.setValue(size[0])
        self.spinbox_y.setValue(size[1])

        if self.main_window.settings.get('clear_languages', False):
            self.clearAllLanguages()
        
        x, y, _ = self.o.size()
        self.table.setColumnCount(y)
        self.table.setRowCount(x)
        self.updateTilesTable()

    def updateTilesTable(self):
        x_base, y_base = self.o.baseCoordinates()
        
        x = self.table.currentRow()
        y = self.table.currentColumn()
        
        self.table.clearContents()

        for i, tile in enumerate(self.o.tiles):
            item = QTableWidgetItem()
            item.setData(QtCore.Qt.UserRole, tile)
            item.setBackground(QtGui.QColor(200, 200, 200) if (tile.x + tile.y) % 2 == 0 else QtGui.QColor(150, 150, 150))
            item.setText(str(i+1))
            item.setTextAlignment(QtCore.Qt.AlignCenter)

            self.table.setItem(x_base + tile.x_orig, y_base + tile.y_orig, item)

        self.table.setCurrentCell(x,y)
        self.setCurrentTile(self.current_tile_index)


    def setCurrentTile(self, tile_index):
        self.current_tile_index = tile_index

        if tile_index is not None:  
            tile = self.o.tiles[tile_index]
            x_base, y_base = self.o.baseCoordinates()
            
            self.table.setCurrentCell(x_base + tile.x_orig, y_base + tile.y_orig)
        self.currentTileChanged(tile_index)

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
        
        for tile in self.o.tiles:
            tile.has_supports = settings_LS.get('hasSupports_LS', False)
            tile.allow_supports_above = settings_LS.get('allowSupportsAbove_LS', False)
            
        self.updateTilesTable()

    def sizeChanged(self, x=None, y=None):
        x_size, y_size, _ = self.o.size()
        
        x_current = self.table.currentRow()
        y_current = self.table.currentColumn()
        if x:
            if x >= x_size:
                self.table.setRowCount(x)
                if x_current >= x:
                    self.table.setCurrentCell(x-1, y_current)
            else:
                self.spinbox_x.setValue(x_size)
            
        if y:
            if y >= y_size:
                self.table.setColumnCount(y)
                if y_current >= y:
                    self.table.setCurrentCell(x_current, y-1)
            else:
                self.spinbox_y.setValue(y_size)

    def cellClicked(self, row, column):
        tile, index = self.o.getTile((row, column))
        if index is not None:
            self.current_tile_index = index
            
            if self.sprites_tab.view_mode == self.sprites_tab.ViewMode.TILES:
                self.sprites_tab.layers.setActiveRow(index, emit_signal=False)
                self.object_tab.activeLayerRowChanged.emit(index)
        else:
            self.current_tile_index = None
            
        self.currentTileChanged(self.current_tile_index)
        
    def currentTileChanged(self, index):
        if index is None:
            self.button_add_tile.setEnabled(True)
            self.button_remove_tile.setEnabled(False)
            
            self.findChild(QGroupBox, "groupBox_tilesettings").setEnabled(False)
                       
            for button in self.buttons_corners:
                button.setChecked(False)
            for button in self.buttons_walls:
                button.setChecked(False)
            
            return
        else:
            tile = self.o.tiles[index]
            self.button_add_tile.setEnabled(False)
            self.button_remove_tile.setEnabled(True if index != 0 else False)
            
            self.findChild(QGroupBox, "groupBox_tilesettings").setEnabled(True)
            self.spinbox_tile_z.setValue(tile.z)
            self.spinbox_tile_h.setValue(tile.h)
            
            self.checkbox_allow_supports.setChecked(tile.allow_supports_above)
            self.checkbox_allow_supports.setEnabled(tile.has_supports)
            self.checkbox_has_supports.setChecked(tile.has_supports)

            for i, button in enumerate(self.buttons_corners):
                button.setChecked(tile.corners[i])
            for i, button in enumerate(self.buttons_walls):
                button.setChecked(not tile.walls[i])
                
    def checkboxTileSyncChanged(self, state):
        if state == QtCore.Qt.Checked:
            tile_base = self.giveCurrentTile()
            for tile in self.o.tiles:
                tile.z = tile_base.z
                tile.h = tile_base.h
                tile.has_supports = tile_base.has_supports
                tile.allow_supports_above = tile_base.allow_supports_above
        
            
    def tileSpinBoxChanged(self, value, name):
        if self.checkbox_tile_sync.isChecked():
            for tile in self.o.tiles:
                if name == 'z':
                    tile.z = value
                elif name == 'h':
                    tile.h = value
        else:
            tile = self.giveCurrentTile()
            if tile is None:
                return
            
            if name == 'z':
                tile.z = value
            elif name == 'h':
                tile.h = value

        self.sprites_tab.updateBoundingBox()
        self.sprites_tab.updateLockedSpriteLayersModel()
        self.sprites_tab.updateAllViews()

    def toggleCorner(self, val, index):
        tile = self.giveCurrentTile()
        if tile:
            tile.corners[index] = val

    def toggleWall(self, val, index):
        tile = self.giveCurrentTile()
        if tile:
            tile.walls[index] = not val

    def tileFlagChanged(self, state, flag):
        if self.checkbox_tile_sync.isChecked():
            for tile in self.o.tiles:
                if flag == 'allowSupports':
                    tile.allow_supports_above = True if state == QtCore.Qt.Checked else False
                elif flag == 'hasSupports':
                    tile.has_supports = True if state == QtCore.Qt.Checked else False
                    self.checkbox_allow_supports.setEnabled((state == QtCore.Qt.Checked))
        else:
            tile = self.giveCurrentTile()
            
            if tile:
                if flag == 'allowSupports':
                    tile.allow_supports_above = True if state == QtCore.Qt.Checked else False
                elif flag == 'hasSupports':
                    tile.has_supports = True if state == QtCore.Qt.Checked else False
                    self.checkbox_allow_supports.setEnabled((state == QtCore.Qt.Checked))

            
    def addTile(self):
        if self.current_tile_index is not None:
            return
        
        x_base, y_base = self.o.baseCoordinates()
        x = self.table.currentRow() - x_base
        y = self.table.currentColumn() - y_base
        
        tile_dict = {
            'clearance': self.spinbox_tile_h.value()*8 if self.checkbox_tile_sync.isChecked() else 0,
            'z': self.spinbox_tile_z.value()*8 if self.checkbox_tile_sync.isChecked() else 0,
            'hasSupports': self.checkbox_has_supports.isChecked() if self.checkbox_tile_sync.isChecked() else self.main_window.settings.get('large_scenery_defaults', {}).get('hasSupports_LS', False),
            'allowSupportsAbove': self.checkbox_allow_supports.isChecked() if self.checkbox_tile_sync.isChecked() else self.main_window.settings.get('large_scenery_defaults', {}).get('allowSupportsAbove_LS', False)
        }
        print(tile_dict)
        self.o.addTile((x, y), tile_dict)
        self.current_tile_index = len(self.o.tiles) - 1
        
        self.sprites_tab.updateBoundingBox()
        self.sprites_tab.updateLockedSpriteLayersModel()
        self.sprites_tab.updateAllViews()
        self.updateTilesTable()
        
    def removeTile(self):
        if self.current_tile_index is None or self.current_tile_index == 0:
            return
        
        self.o.removeTile(self.current_tile_index)
        self.current_tile_index = None
        self.sprites_tab.updateBoundingBox()
        self.sprites_tab.updateLockedSpriteLayersModel()
        self.sprites_tab.updateAllViews()
        self.updateTilesTable()

        
    def fillShape(self):
        x_base, y_base = self.o.baseCoordinates()
        x_length = self.table.rowCount()
        y_length = self.table.columnCount()

        tile_dict = {
            'clearance': self.spinbox_tile_h.value()*8 if self.checkbox_tile_sync.isChecked() else 0,
            'z': self.spinbox_tile_z.value()*8 if self.checkbox_tile_sync.isChecked() else 0,
            'hasSupports': self.checkbox_has_supports.isChecked() if self.checkbox_tile_sync.isChecked() else self.main_window.settings.get('large_scenery_defaults', {}).get('hasSupports_LS', False),
            'allowSupportsAbove': self.checkbox_allow_supports.isChecked() if self.checkbox_tile_sync.isChecked() else self.main_window.settings.get('large_scenery_defaults', {}).get('allowSupportsAbove_LS', False)
        }

        self.o.fillShape(x_length, y_length, base_x=x_base, base_y=y_base, dict_entry=tile_dict)

        self.sprites_tab.updateBoundingBox()
        self.sprites_tab.updateLockedSpriteLayersModel()
        self.sprites_tab.updateAllViews()
        self.updateTilesTable()
        
    def detectInnerBorders(self):
        self.o.detectWalls()
        
        self.updateTilesTable()


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

        self.createLayers()

        self.previewClicked(0)
        self.updateAllViews()

    def save(self):
        if self.view_mode == self.ViewMode.PROJECTION:
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
            self.object_tab.settings_tab.checkbox_tile_sync.setChecked(True)
            self.object_tab.settings_tab.checkbox_tile_sync.setEnabled(False)
        elif mode == self.ViewMode.TILES:
            self.projectSprites()
            self.object_tab.settings_tab.checkbox_tile_sync.setEnabled(True)
            
        self.updateBoundingBox()
        self.updateLockedSpriteLayersModel()

    def activeLayerRowChanged(self, row):
        if self.view_mode == self.ViewMode.TILES:
            self.object_tab.settings_tab.setCurrentTile(row)

        self.updateBoundingBox()


    def getTileLayerById(self, id):
        return self.layers.item(id)

    def createLayers(self):
        
        if self.view_mode == self.ViewMode.PROJECTION:
            self.layers = wdg.SpriteLayerModel(1, 4)
            for rot in range(4):
                sprite = self.projectionSprites[rot]
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, 0, 0, 0, 0, name=f'View {rot+1}')
                self.layers.setItem(0, rot, layer)
        elif self.view_mode == self.ViewMode.TILES:
            center_x, center_y = self.o.centerOffset()
            orders = [list(reversed(self.o.getDrawingOrder(rotation=rot))) for rot in range(4)]
            
            self.layers = wdg.SpriteLayerModel(self.o.numTiles(), 4, orders=orders)
            
            for rot in range(4):
                for tile_entry in self.o.getOrderedTileSprites(rotation=rot):
                    layer = wdg.SpriteLayer(
                        tile_entry[0], self.main_window, 0, 0, -center_x+tile_entry[1], -center_y+tile_entry[2], name=f'View {rot+1} Tile {tile_entry[3]+1}')
                    self.layers.setItem(tile_entry[3], rot, layer)
            
            try:
                if self.object_tab.settings_tab.current_tile_index is not None:
                    self.layers.setActiveRow(self.object_tab.settings_tab.current_tile_index, emit_signal=False)
                else: 
                    self.layers.setActiveRow(0, emit_signal=False)
            except AttributeError:
                self.layers.setActiveRow(0, emit_signal=False)
                
            self.layers.activeRowChanged.connect(self.activeLayerRowChanged)
            
        self.layers.setActiveColumn(self.o.rotation)

    def requestNumberOfLayers(self):
        return self.o.numTiles() if self.view_mode == self.ViewMode.TILES else 1

    # def setCurrentLayers(self, layers, view=None):
    #     #TODO
    #     if view == None:
    #         view = self.o.rotation

    #     if self.requestNumberOfLayers() != layers.rowCount():
    #         dialog = SpriteImportUi(layers, self.layers[view])

    #         if dialog.exec():
    #             target_index = dialog.selected_index
    #             layers_incoming = dialog.selected_incoming

    #             if len(layers_incoming) == 0:
    #                 return

    #             layer_top = layers_incoming[0]
    #             for i in range(len(layers_incoming)-1):
    #                 layer_bottom = layers_incoming[i+1]
    #                 layer_bottom.merge(layer_top)
    #                 layer_top = layer_bottom

    #             target_layer = self.layers[view][target_index]
    #             target_layer.sprite.setFromSprite(layer_top.sprite)

    #         else:
    #             return
    #     else:
    #         for i in range(layers.rowCount()):
    #             index = layers.rowCount() - i - 1
    #             target_layer = self.layers[view][i]
    #             target_layer.sprite.setFromSprite(layers.item(
    #                 index, 0).sprite)

    #     if self.object_tab.locked:
    #         self.createLayers()
    #         self.object_tab.locked_sprite_tab.updateLayersModel()

    #     self.updateMainView()


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
        
    def updateBoundingBox(self):
        try:
            dummy_o, dummy_coords = self.object_tab.giveDummy()
        except AttributeError:
            return

        backbox, coords = self.main_window.bounding_boxes.giveBackbox(dummy_o)
        self.object_tab.boundingBoxChanged.emit(
            self.main_window.layer_widget.button_bounding_box.isChecked(), backbox, (coords[0]+dummy_coords[0], coords[1] + dummy_coords[1]))


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


class TileItem(QtGui.QStandardItem):
    def __init__(self, tile):
        super().__init__()
        self.tile = tile
        self.setText(f"Tile {tile.x}, {tile.y}")
