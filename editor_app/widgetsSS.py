# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QFileDialog
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

        # Clearence Spinbox
        self.clearence_box = self.findChild(QSpinBox, "spinBox_clearence")
        self.clearence_box.valueChanged.connect(self.clearenceChanged)

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
        self.sprites_tab.updateMainView()

    def clearenceChanged(self, value):
        self.o['properties']['height'] = value*8
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

        self.clearence_box.setValue(int(self.o['properties']['height']/8))

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

        # Buttons auxiliary
        self.button_bounding_box = self.findChild(
            QToolButton, "toolButton_boundingBox")
        self.button_symm_axes = self.findChild(
            QToolButton, "toolButton_symmAxes")

        self.button_bounding_box.clicked.connect(self.updateMainView)
        self.button_symm_axes.clicked.connect(self.updateMainView)

        # Sprite control buttons
        self.button_sprite_left = self.findChild(
            QToolButton, "toolButton_left")
        self.button_sprite_down = self.findChild(
            QToolButton, "toolButton_down")
        self.button_sprite_right = self.findChild(
            QToolButton, "toolButton_right")
        self.button_sprite_up = self.findChild(
            QToolButton, "toolButton_up")
        self.button_sprite_left_right = self.findChild(
            QToolButton, "toolButton_leftright")
        self.button_sprite_up_down = self.findChild(
            QToolButton, "toolButton_updown")

        self.button_sprite_left.clicked.connect(
            lambda x: self.clickSpriteControl('left'))
        self.button_sprite_down.clicked.connect(
            lambda x: self.clickSpriteControl('down'))
        self.button_sprite_right.clicked.connect(
            lambda x: self.clickSpriteControl('right'))
        self.button_sprite_up.clicked.connect(
            lambda x: self.clickSpriteControl('up'))
        self.button_sprite_left_right.clicked.connect(
            lambda x: self.clickSpriteControl('leftright'))
        self.button_sprite_up_down.clicked.connect(
            lambda x: self.clickSpriteControl('updown'))

        icon = QtGui.QPixmap()
        icon.loadFromData(
            get_data("customwidgets", 'res/icon_reflectionLR.png'), 'png')
        self.button_sprite_left_right.setIcon(QtGui.QIcon(icon))

        icon = QtGui.QPixmap()
        icon.loadFromData(
            get_data("customwidgets", 'res/icon_reflectionUD.png'), 'png')
        self.button_sprite_up_down.setIcon(QtGui.QIcon(icon))

        self.button_cycle_rotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")

        self.button_cycle_rotation.clicked.connect(self.cycleRotation)

        self.sprite_view_main.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sprite_view_main.customContextMenuRequested.connect(
            self.showSpriteMenu)
        self.sprite_view_main.setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color};")

        self.offset = 16 if (self.o.shape == obj.SmallScenery.Shape.QUARTER or self.o.shape ==
                             obj.SmallScenery.Shape.QUARTERD) else 32
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
            print(self.main_window.current_import_color)
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
        for rot in range(4):
            self.updatePreview(rot)

        self.updateMainView()

    def previewClicked(self, rot):
        old_rot = self.o.rotation
        self.sprite_preview[old_rot].setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color}; border:2px outset rgb{self.main_window.current_background_color};")
        self.sprite_preview[rot].setStyleSheet(
            f"background-color :  rgb{self.main_window.current_background_color}; border:2px outset green;")

        self.o.rotateObject(rot)

        self.updateMainView()

    def clickSpriteControl(self, direction: str):
        sprite = self.o.giveSprite()

        if direction == 'left':
            sprite.x -= 1
        elif direction == 'right':
            sprite.x += 1
        elif direction == 'up':
            sprite.y -= 1
        elif direction == 'down':
            sprite.y += 1
        elif direction == 'leftright':
            sprite.image = sprite.image.transpose(
                Image.FLIP_LEFT_RIGHT)
        elif direction == 'updown':
            sprite.image = sprite.image.transpose(
                Image.FLIP_TOP_BOTTOM)

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

    def updateMainView(self):
        im, x, y = self.o.show()

        coords = (76+x, 200+y)

        canvas = Image.new('RGBA', (152, 271))

        if self.button_bounding_box.isChecked():
            backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(
                self.o)
            canvas.paste(
                backbox, (76+coords_backbox[0], 200+coords_backbox[1]), backbox)

        canvas.paste(im, coords, im)

        if self.button_symm_axes.isChecked():
            symm_axis, coords_symm_axis = self.main_window.symm_axes.giveSymmAxes(
                self.o)
            canvas.paste(
                symm_axis, (76+coords_symm_axis[0], 200+coords_symm_axis[1]), symm_axis)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main.setPixmap(pixmap)

        if self.object_tab.locked:
            self.object_tab.locked_sprite_tab.updateView(skip_locked=True)

        self.updatePreview(self.o.rotation)

    def giveMainView(self, canvas_size, add_auxiliaries):
        im, x, y = self.o.show()

        canvas = Image.new('RGBA', (canvas_size, canvas_size))

        if add_auxiliaries and self.button_bounding_box.isChecked():
            backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(
                self.o)
            canvas.paste(backbox, (int(
                canvas_size/2)+coords_backbox[0], int(canvas_size*2/3)+coords_backbox[1]), backbox)

        coords = (int(canvas_size/2)+x, int(canvas_size*2/3)+y)

        canvas.paste(im, coords, im)

        if add_auxiliaries and self.button_symm_axes.isChecked():
            symm_axis, coords_symm_axis = self.main_window.symm_axes.giveSymmAxes(
                self.o)
            canvas.paste(symm_axis, (int(
                canvas_size/2)+coords_symm_axis[0], int(canvas_size*2/3)+coords_symm_axis[1]), symm_axis)

        return canvas

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
