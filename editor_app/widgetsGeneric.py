# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2024 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""
from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QListWidgetItem, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PIL import Image, ImageGrab, ImageDraw
from PIL.ImageQt import ImageQt
from copy import copy, deepcopy
import io
import os.path
import sip
from os import getcwd
import numpy as np
from pkgutil import get_data


import auxiliaries as aux
import widgets as wdg

from customwidgets import RemapColorSelectButton, ColorSelectWidget, ToolBoxWidget

import customwidgets as cwdg

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal
from rctobject import objects as obj


class SettingsTabAll(QWidget):
    """Proxy Class for all object types. initializeWidgets should be called after all members have been set."""

    def __init__(self, o, object_tab, sprites_tab):
        super().__init__()

        self.o = o
        self.object_tab = object_tab
        self.sprites_tab = sprites_tab
        self.main_window = object_tab.main_window

    def initializeWidgets(self):
        tab_naming_misc = TabNamingMisc()

        self.tab_widget.addTab(tab_naming_misc, 'Names and Misc.')

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
        self.scenery_group_id_field = self.findChild(
            QLineEdit, "lineEdit_sceneryGroupID")
        self.mirror_object_id_field = self.findChild(
            QLineEdit, "lineEdit_mirrorID")

        self.button_copy_id = self.findChild(QPushButton, "pushButton_copyID")

        self.name_lang_box = self.findChild(
            QComboBox, "comboBox_languageSelect")
        self.name_lang_box.currentIndexChanged.connect(self.languageChanged)
        self.language_index = 0

        self.button_clear_all_languages = self.findChild(
            QPushButton, "pushButton_clearAllLang")
        self.button_clear_all_languages.clicked.connect(self.clearAllLanguages)

        self.author_field.textChanged.connect(self.authorChanged)
        self.author_id_field.textEdited.connect(self.authorIdChanged)
        self.object_id_field.textChanged.connect(self.idChanged)
        self.object_name_field.textChanged.connect(self.nameChanged)
        self.object_name_lang_field.textChanged.connect(self.nameChangedLang)
        self.scenery_group_id_field.textChanged.connect(
            self.sceneryGroupIdChanged)
        self.mirror_object_id_field.textChanged.connect(self.mirrorIdChanged)

        self.button_copy_id.clicked.connect(self.copyIdToClipboard)

        # Curser combobox
        self.cursor_box = self.findChild(QComboBox, "comboBox_cursor")

        for cursor in cts.cursors:
            self.cursor_box.addItem(cursor.replace('_', ' '))

        self.cursor_box.currentIndexChanged.connect(self.cursorChanged)

        # Remap check
        checkbox = self.findChild(QCheckBox, 'checkBox_remapCheck')
        checkbox.stateChanged.connect(self.flagRemapChanged)

    def save(self):
        if self.checkBox_remapCheck.isChecked():
            for path, sprite in self.o.sprites.items():
                if sprite.checkPrimaryColor():
                    self.o['properties']['hasPrimaryColour'] = True
                    break
            for path, sprite in self.o.sprites.items():
                if sprite.checkSecondaryColor():
                    self.o['properties']['hasSecondaryColour'] = True
                    break
            for path, sprite in self.o.sprites.items():
                if sprite.checkTertiaryColor():
                    self.o['properties']['hasTertiaryColour'] = True
                    break

    def tabChanged(self, index):
        if index == 0:
            self.object_name_field.setText(self.o['strings']['name']['en-GB'])
        elif index == 2 and self.language_index == 0:
            self.object_name_lang_field.setText(
                self.o['strings']['name']['en-GB'])

    def cursorChanged(self):
        value = self.cursor_box.currentIndex()

        self.o['properties']['cursor'] = cts.cursors[value]

    def spinBoxChanged(self, value, name):
        if name == 'version':
            self.o['version'] = str(value)
        else:
            self.o['properties'][name] = value

    def flagChanged(self, value, flag):
        self.o.changeFlag(flag, bool(value))

        self.sprites_tab.updateMainView()

    def flagRemapChanged(self, value):
        self.hasPrimaryColour.setEnabled(not bool(value))
        self.hasSecondaryColour.setEnabled(not bool(value))
        self.hasTertiaryColour.setEnabled(not bool(value))

    def authorChanged(self, value):
        self.o['authors'] = value.replace(' ', '').split(',')

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

    def sceneryGroupIdChanged(self, value):
        self.o['properties']['sceneryGroup'] = value

    def mirrorIdChanged(self, value):
        self.o['properties']['mirrorObjectId'] = value

    def copyIdToClipboard(self):
        QApplication.clipboard().setText(self.o['id'])

    def nameChanged(self, value):
        self.o['strings']['name']['en-GB'] = value

    def clearAllLanguages(self):
        for lang in self.o['strings']['name'].keys():
            if lang != 'en-GB':
                self.o['strings']['name'][lang] = ''
        if self.language_index != 0:
            self.object_name_lang_field.setText('')

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


class SpritesTabAll(QWidget):
    """Proxy Class for all object types. initializeWidgets should be called after all members have been set."""

    def __init__(self, o, object_tab):
        super().__init__()

        self.o = o
        self.object_tab = object_tab
        self.main_window = object_tab.main_window
        self.last_image_path = ''

    def initializeWidgets(self, view_width, view_height):
        # Buttons load/reset
        self.button_load_image = self.findChild(
            QPushButton, "pushButton_loadImage")

        self.button_load_image.clicked.connect(self.loadImage)

        self.button_cycle_rotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")

        self.button_cycle_rotation.clicked.connect(self.cycleRotation)

        # View main
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
        self.sprite_view_main_scene.setSceneRect(0, 0, view_width, view_height)
        self.sprite_view_main.setScene(self.sprite_view_main_scene)

        # Previews
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

    def save(self):
        # method to prepare sprites for saving to be defined in sub class
        pass

    def setImage(self, image):
        image = image.convert('RGBA')

        selected_colors = self.main_window.tool_widget.color_select_panel.selectedColors()

        if self.main_window.current_import_offset_mode == 'bottom':
            x, y, _ = self.o.size()
            offset_y = (16*x+16*y)//2
        else:
            offset_y = 0

        sprite = spr.Sprite(image,
                            palette=self.main_window.current_palette,
                            transparent_color=self.main_window.current_import_color,
                            selected_colors=selected_colors,
                            alpha_threshold=0,
                            offset=(0, offset_y),
                            auto_offset_mode=self.main_window.current_import_offset_mode)

        layer = wdg.SpriteLayer(sprite, self.main_window, 0, 0)

        layers = QtGui.QStandardItemModel()
        layers.insertRow(0, layer)

        self.setCurrentLayers(layers)

    def loadImage(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", self.last_image_path, "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            image = Image.open(filepath)

            self.setImage(image)

            self.last_image_path, _ = os.path.split(filepath)

        self.updateLockedSpriteLayersModel()
        self.updateMainView()

    def resetImage(self):
        for layer in self.giveCurrentMainViewLayers():
            layer.sprite.resetSprite()

        self.updateMainView()

    def resetOffsets(self):
        for layer in self.giveCurrentMainViewLayers():
            layer.sprite.resetOffsets()

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

        # submenu_copy.addAction("All Frames of View",
        #                        self.copySpriteToAllFramesView)

        menu.addMenu(submenu_copy)

        menu.addAction("Delete Sprite", self.deleteSprite)

        menu.exec_(self.sprite_view_main.mapToGlobal(pos))

    def pasteSpriteFromClipboard(self):
        if self.main_window.sprite_clipboard:
            self.setCurrentLayers(self.main_window.sprite_clipboard)
        else:
            image = ImageGrab.grabclipboard()
            if type(image) == list:
                try:
                    image = Image.open(image[0])
                except:
                    return

            if image:
                self.setImage(image)

        self.updateLockedSpriteLayersModel()
        self.updateMainView()

    def copySpriteToClipboard(self):
        pixmap = self.sprite_view_main_item.pixmap()

        QApplication.clipboard().setPixmap(pixmap)
        layers = QtGui.QStandardItemModel()

        for i, layer in enumerate(self.giveCurrentMainViewLayers()):
            layers.insertRow(i, wdg.SpriteLayer.fromLayer(layer))

        self.main_window.sprite_clipboard = layers
        self.main_window.sprite_clipboard_reset = False

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

    def updateLockedSpriteLayersModel(self):
        if self.object_tab.locked:
            self.createLayers()
            self.object_tab.locked_sprite_tab.updateLayersModel()
            self.updateAllViews()

    def giveCurrentMainViewLayers(self):
        return self.layers[self.o.rotation]

    def updateMainView(self):
        # to be defined in sub class
        pass

    def updatePreview(self, rot):
        # to be defined in sub class
        pass

    def updateAllViews(self):
        self.updateMainView()
        for rot in range(4):
            self.updatePreview(rot)


class TabNamingMisc(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/tab_naming_misc.ui'), self)
