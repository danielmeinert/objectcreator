# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QMenu, QGroupBox, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget, QFileDialog, QGraphicsPixmapItem, QGraphicsScene
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

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal
from rctobject import objects as obj


class SettingsTab(QWidget):
    def __init__(self, o, object_tab, sprites_tab, author, author_id):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/settingsSS.ui'), self)

        self.o = o
        self.object_tab = object_tab
        self.sprites_tab = sprites_tab
        self.main_window = object_tab.main_window

        self.tab_widget = self.findChild(QTabWidget, "tabWidget_settingsSS")
        self.tab_widget.currentChanged.connect(self.tabChanged)

        self.button_set_defaults = self.findChild(
            QPushButton, "pushButton_applyDefaultSettings")
        self.button_set_defaults.clicked.connect(self.setDefaults)

        # Subtype combobox, for now only simple available
        self.subtype_box = self.findChild(
            QComboBox, "comboBox_subtype")

        self.subtype_box.currentIndexChanged.connect(self.subtypeChanged)

        for i in [1, 2, 3]:
            self.subtype_box.model().item(i).setEnabled(False)

        # Shape combobox
        self.shape_box = self.findChild(
            QComboBox, "comboBox_shape")
        self.diagonal_box = self.findChild(QCheckBox, "checkBox_diagonal")

        self.shape_box.currentIndexChanged.connect(self.shapeChanged)
        self.diagonal_box.stateChanged.connect(self.shapeChanged)

        # clearance Spinbox
        self.clearance_box = self.findChild(QSpinBox, "spinBox_clearance")
        self.clearance_box.valueChanged.connect(self.clearanceChanged)

        # Curser combobox
        self.cursor_box = self.findChild(QComboBox, "comboBox_cursor")

        for cursor in cts.cursors:
            self.cursor_box.addItem(cursor.replace('_', ' '))

        # Names
        self.author_field = self.findChild(QLineEdit, "lineEdit_author")
        self.author_id_field = self.findChild(QLineEdit, "lineEdit_authorID")
        self.object_id_field = self.findChild(QLineEdit, "lineEdit_objectID")
        self.object_original_id_field = self.findChild(
            QLineEdit, "lineEdit_originalID")
        self.object_name_field = self.findChild(
            QLineEdit, "lineEdit_objectName")
        self.object_name_lang_field = self.findChild(
            QLineEdit, "lineEdit_nameInput")

        self.name_lang_box = self.findChild(
            QComboBox, "comboBox_languageSelect")
        self.name_lang_box.currentIndexChanged.connect(self.languageChanged)
        self.language_index = 0

        self.button_clear_all_languages = self.findChild(
            QPushButton, "pushButton_clearAllLang")
        self.button_clear_all_languages.clicked.connect(self.clearAllLanguages)

        self.author_field.textEdited.connect(self.authorChanged)
        self.author_id_field.textEdited.connect(self.authorIdChanged)
        self.object_id_field.textEdited.connect(self.idChanged)
        self.object_name_field.textEdited.connect(self.nameChanged)
        self.object_name_lang_field.textEdited.connect(self.nameChangedLang)

        # Flags
        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.stateChanged.connect(
                    lambda x, flag=checkbox.objectName(): self.flagChanged(x, flag))
        checkbox = self.findChild(QCheckBox, 'isTree')
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

        checkbox = self.findChild(QCheckBox, 'checkBox_remapCheck')
        checkbox.stateChanged.connect(self.flagRemapChanged)

        self.checkbox_keep_dat_id = self.findChild(
            QCheckBox, "checkBox_keepOrginalId")

        self.loadObjectSettings(author=author, author_id=author_id)

    def tabChanged(self, index):
        if index == 0:
            self.object_name_field.setText(self.o['strings']['name']['en-GB'])
        elif index == 2 and self.language_index == 0:
            self.object_name_lang_field.setText(
                self.o['strings']['name']['en-GB'])

    # bother with when other subtypes are introduced
    
    def giveDummy(self):
        dummy_o  = obj.newEmpty(cts.Type.SMALL)
        dummy_o.changeShape(self.o.shape)
        dummy_o['properties']['height'] = int(self.o['properties']['height'])
                        
        return dummy_o

    def subtypeChanged(self, value):
        pass

    def shapeChanged(self):
        value = self.shape_box.currentIndex()
        if value == 0:
            self.diagonal_box.setEnabled(True)
            if self.diagonal_box.isChecked():
                shape = obj.SmallScenery.Shape.QUARTERD
            else:
                shape = obj.SmallScenery.Shape.QUARTER

        elif value == 1:
            self.diagonal_box.setChecked(False)
            self.diagonal_box.setEnabled(False)
            shape = obj.SmallScenery.Shape.HALF

        elif value == 2:
            self.diagonal_box.setChecked(True)
            self.diagonal_box.setEnabled(False)
            shape = obj.SmallScenery.Shape.THREEQ

        elif value == 3:
            self.diagonal_box.setEnabled(True)
            if self.diagonal_box.isChecked():
                shape = obj.SmallScenery.Shape.FULLD
            else:
                shape = obj.SmallScenery.Shape.FULL

        self.o.changeShape(shape)

        backbox, coords = self.main_window.bounding_boxes.giveBackbox(self.o)
        self.object_tab.boundingBoxChanged.emit(
            self.main_window.layer_widget.button_bounding_box.isChecked(), backbox, coords)
        symm_axis, coords = self.main_window.symm_axes.giveSymmAxes(self.o)
        self.object_tab.symmAxesChanged.emit(
            self.main_window.layer_widget.button_symm_axes.isChecked(), symm_axis, coords)
        self.sprites_tab.updateMainView()

    def clearanceChanged(self, value):
        self.o['properties']['height'] = value*8        
 
        backbox, coords = self.main_window.bounding_boxes.giveBackbox(self.o)
        self.object_tab.boundingBoxChanged.emit(
            self.main_window.layer_widget.button_bounding_box.isChecked(), backbox, coords)
        
        self.sprites_tab.updateMainView()

    def authorChanged(self, value):
        self.o['authors'] = value.split(',')

    def authorIdChanged(self, value):
        object_id = self.object_id_field.text()
        object_type = self.o.object_type.value
        self.o['id'] = f'{value}.{object_type}.{object_id}'
        self.object_tab.saved = False

    def idChanged(self, value):
        author_id = self.author_id_field.text()
        object_type = self.o.object_type.value
        self.o['id'] = f'{author_id}.{object_type}.{value}'
        self.object_tab.saved = False

    def nameChanged(self, value):
        self.o['strings']['name']['en-GB'] = value

    def clearAllLanguages(self):
        for lang in self.o['strings']['name'].keys():
            if lang != 'en-GB':
                self.o['strings']['name'][lang] = ''
        self.object_name_lang_field.setText('')

    def spinBoxChanged(self, value, name):
        if name == 'version':
            self.o['version'] = str(value)
        else:
            self.o['properties'][name] = value

    def nameChangedLang(self, value):
        if self.language_index == 0:
            self.o['strings']['name']['en-GB'] = value
            self.object_name_field.setText(value)
        else:
            lang = list(cts.languages)[self.language_index]
            self.o['strings']['name'][lang] = value

    def languageChanged(self, value):
        lang = list(cts.languages)[self.language_index]
        self.o['strings']['name'][lang] = self.object_name_lang_field.text()

        self.language_index = value
        lang = list(cts.languages)[value]
        self.object_name_lang_field.setText(
            self.o['strings']['name'].get(lang, ''))

    def flagChanged(self, value, flag):
        self.o.changeFlag(flag, bool(value))

        self.sprites_tab.updateMainView()

    def flagRemapChanged(self, value):
        self.hasPrimaryColour.setEnabled(not bool(value))
        self.hasSecondaryColour.setEnabled(not bool(value))
        self.hasTertiaryColour.setEnabled(not bool(value))

    def loadObjectSettings(self, author=None, author_id=None):

        self.subtype_box.setCurrentIndex(self.o.subtype.value)

        shape = self.o.shape

        if shape == obj.SmallScenery.Shape.FULLD:
            self.shape_box.setCurrentIndex(3)
            self.diagonal_box.setChecked(True)
        elif shape == obj.SmallScenery.Shape.QUARTERD:
            self.shape_box.setCurrentIndex(0)
            self.diagonal_box.setChecked(True)
        else:
            self.shape_box.setCurrentIndex(shape.value)

        self.clearance_box.setValue(int(self.o['properties']['height']/8))

        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(self.o['properties'].get(flag, False))

        checkbox = self.findChild(QCheckBox, 'isTree')
        checkbox.setChecked(self.o['properties'].get('isTree', False))
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

        settings_SS = self.main_window.settings['small_scenery_defaults']

        for flag in settings_SS:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(settings_SS.get(flag, False))

        self.spinbox_price.setValue(settings_SS.get('price', 1))
        self.spinbox_removal_price.setValue(settings_SS.get('removalPrice', 1))
        self.spinbox_version.setValue(settings_SS.get('version', 1.0))

        self.cursor_box.setCurrentIndex(cts.cursors.index(
            settings_SS.get('cursor', 'CURSOR_BLANK')))


class SpritesTab(QWidget):
    def __init__(self, o, object_tab):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/spritesSS.ui'), self)

        self.o = o
        self.object_tab = object_tab
        self.main_window = object_tab.main_window

        # Buttons load/reset
        self.button_load_image = self.findChild(
            QPushButton, "pushButton_loadImage")
        self.button_reset_image = self.findChild(
            QPushButton, "pushButton_resetImage")
        self.button_reset_offsets = self.findChild(
            QPushButton, "pushButton_resetOffsets")

        self.button_load_image.clicked.connect(self.loadImage)
        self.button_reset_image.clicked.connect(self.resetImage)
        self.button_reset_offsets.clicked.connect(self.resetOffsets)

        self.button_cycle_rotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")

        self.button_cycle_rotation.clicked.connect(self.cycleRotation)

        self.sprite_view_main.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sprite_view_main.customContextMenuRequested.connect(
            self.showSpriteMenu)
        self.sprite_view_main.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(self.main_window.current_background_color[0],
                                          self.main_window.current_background_color[1],
                                          self.main_window.current_background_color[2])))
        
        self.sprite_view_main_item = QGraphicsPixmapItem()
        self.sprite_view_main_scene = QGraphicsScene()
        self.sprite_view_main_scene.addItem(self.sprite_view_main_item)
        self.sprite_view_main_scene.setSceneRect(0,0,151,268)
        self.sprite_view_main.setScene(self.sprite_view_main_scene)

        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1,
                               self.sprite_view_preview2, self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent = (
                lambda e, rot=rot: self.previewClicked(rot))
            self.sprite_preview[rot].setStyleSheet(
                f"background-color :  rgb{self.main_window.current_background_color};")

            self.updatePreview(rot)

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

        self.previewClicked(0)

    def loadImage(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            sprite = spr.Sprite.fromFile(filepath, palette=self.main_window.current_palette,
                                         use_transparency=True, transparent_color=self.main_window.current_import_color)
            self.o.setSprite(sprite)

        self.updateMainView()

    def resetImage(self):
        sprite = self.o.giveSprite()
        sprite.resetSprite()

        self.updateMainView()

    def resetOffsets(self):
        sprite = self.o.giveSprite()
        sprite.resetOffsets()

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

        if image:
            sprite = spr.Sprite(image, palette=self.main_window.current_palette,
                                use_transparency=True, transparent_color=self.main_window.current_import_color)
            self.o.setSprite(sprite)

        self.updateMainView()

    def copySpriteToClipboard(self):
        sprite = self.o.giveSprite()

        image = ImageQt(sprite.image)
        pixmap = QtGui.QPixmap.fromImage(image)

        QApplication.clipboard().setPixmap(pixmap)

    def copySpriteToView(self, view):
        self.o.setSprite(self.o.giveSprite(), rotation=view)

        self.updatePreview(view)

    def copySpriteToAllViews(self):
        rot = self.o.rotation

        for view in range(3):
            self.o.setSprite(self.o.giveSprite(),
                             rotation=(rot + view + 1) % 4)

        self.updateAllViews()

    def deleteSprite(self):
        sprite = spr.Sprite(None, palette=self.main_window.current_palette)
        self.o.setSprite(sprite)

        self.updateMainView()

    def cycleRotation(self):
        self.o.cycleSpritesRotation()

        if self.object_tab.locked:
            self.createLayers(self.object_tab.locked_sprite_tab.base_x,
                              self.object_tab.locked_sprite_tab.base_y)
            self.object_tab.locked_sprite_tab.updateLayersModel()

        self.updateAllViews()

    def previewClicked(self, rot):
        old_rot = self.o.rotation
        self.sprite_preview[old_rot].setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color}; border:2px outset rgb{self.main_window.current_background_color};")
        self.sprite_preview[rot].setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color}; border:2px outset green;")

        self.o.rotateObject(rot)

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
        
        if self.o.subtype == obj.SmallScenery.Subtype.GLASS:
            for rot in range(4):
                sprite = self.o.giveSprite(rotation = rot)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, base_x, base_y, name = f'Structure View {rot+1}')
                self.layers[rot].append(layer)
            for rot in range(4):
                sprite = self.o.giveSprite(rotation = rot, glass = True)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, base_x, base_y, name = f'Glass View {rot+1}')
                self.layers[rot].append(layer)

        else:    
            for rot in range(4):
                sprite = self.o.giveSprite(rotation = rot)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, base_x, base_y, name = f'View {rot+1}')
                self.layers[rot].append(layer)
                
    def giveCurrentMainViewLayers(self, base_x, base_y):
        return self.layers[self.o.rotation]

    def requestNumberOfLayers(self):
        if self.o.subtype == self.o.Subtype.SIMPLE:
            return 1
        elif self.o.subtype == self.o.Subtype.ANIMATED:
            raise NotImplementedError("Subtype missing")
        elif self.o.subtype == self.o.Subtype.GLASS:
            return 2
        elif self.o.subtype == self.o.Subtype.GARDENS:
            return 3

    def setCurrentLayers(self, layers):
        if self.requestNumberOfLayers() != layers.rowCount():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Layers number does not match!")
            msg.setTextFormat(QtCore.Qt.RichText)

            msg.setText(
                f"The number of layers of current sprite does not match the required number of layers for this object type. <br> \
                    Do you want to merge all layers and push to main layer of object?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            reply = msg.exec_()

            if reply == QMessageBox.Yes:
                layer_top = layers.item(0,0)
                for i in range(layers.rowCount()-1):
                    layer_bottom = layers.item(i+1,0)
                    layer_bottom.merge(layer_top)
                    layer_top = layer_bottom
                    
                self.layers[self.o.rotation][0] = wdg.SpriteLayer.fromLayer(layer_bottom)
            else:
                return
        else:
            for i in range(layers.rowCount()):                
                self.o.setSpriteFromIndex(layers.item(i,0).sprite, i*4+self.o.rotation)
                
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
        self.sprite_view_main_scene.setSceneRect(0,0,151,height)
        
        coords = (76+x, height-70+y)

        image = ImageQt(im)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main_item.setOffset(coords[0],coords[1])
        
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
        canvas.paste(im, coords, im)
        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)

    def updateAllViews(self):
        self.updateMainView()
        for rot in range(4):
            self.updatePreview(rot)
