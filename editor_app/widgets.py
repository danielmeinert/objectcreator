# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""
from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget, QFileDialog
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

from customwidgets import RemapColorSelectWidget
import customwidgets as cwdg

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal
from rctobject import objects as obj




class ObjectTabSS(QWidget):
    def __init__(self, o, main_window, filepath = None, author = None, author_id = None):
        super().__init__()

        self.o = o
        self.lastpath = filepath
        self.saved = False
        self.main_window = main_window

        self.locked = False
        self.locked_sprite_tab = False


        layout = QHBoxLayout()

        self.sprites_tab = SpritesTabSS(o, self)
        self.settings_tab = SettingsTabSS(o, self, self.sprites_tab, author, author_id)

        layout.addWidget(self.sprites_tab)
        layout.addWidget(self.settings_tab)

        self.setLayout(layout)

    def saveObject(self, get_path):

        name = self.o.data.get('id','')

        if get_path or not self.saved:
            if self.lastpath:
                folder = self.lastpath
                path = f"{self.lastpath}/{name}.parkobj"
            else:
                folder = self.main_window.settings.get('savedefault','')
                if not folder:
                    folder = getcwd()
                path = f"{folder}/{name}.parkobj"

            filepath, _ = QFileDialog.getSaveFileName(self, "Save Object", path, "Parkobj Files (*.parkobj)")
            while filepath.endswith('.parkobj'):
                filepath = filepath[:-8]
            filepath, name = os.path.split(filepath)
        else:
            filepath = self.lastpath

        if self.settings_tab.checkBox_remapCheck.isChecked():
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

        if filepath:
            self.lastpath = filepath
            self.o.save(filepath, name = name, no_zip = self.main_window.settings['no_zip'], include_originalId = self.settings_tab.checkbox_keep_dat_id.isChecked())
            self.saved = True

    def lockWithSpriteTab(self, locked_sprite_tab):
        if self.locked:
            self.unlockSpriteTab()

        self.locked = True
        self.locked_sprite_tab = locked_sprite_tab

    def unlockSpriteTab(self):
        self.locked = False
        self.locked_sprite_tab = None

    def giveCurrentMainViewSprite(self):
        return self.o.giveSprite(return_index = True)

    def giveCurrentMainView(self, canvas_size = 200, add_auxilaries = False):
        return self.sprites_tab.giveMainView(canvas_size, add_auxilaries)

    def updateCurrentMainView(self):
        self.sprites_tab.updateMainView()

    def setCurrentSprite(self, sprite):
        self.o.setSprite(sprite)
        self.updateCurrentMainView()

    def colorRemapToAll(self, color_remap, selected_colors):
        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.remapColor(color, color_remap)

        self.sprites_tab.updateAllViews()

    def colorChangeBrightnessAll(self, step, selected_colors):
        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.changeBrightnessColor(step, color)

        self.sprites_tab.updateAllViews()

    def colorRemoveAll(self, selected_colors):
        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.removeColor(color)

        self.sprites_tab.updateAllViews()



class SettingsTabSS(QWidget):
    def __init__(self, o, object_tab, sprites_tab, author, author_id):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/settingsSS.ui'), self)

        self.o = o
        self.object_tab = object_tab
        self.sprites_tab = sprites_tab
        self.main_window = object_tab.main_window

        self.tab_widget = self.findChild(QTabWidget, "tabWidget_settingsSS")
        self.tab_widget.currentChanged.connect(self.tabChanged)

        self.button_set_defaults = self.findChild(QPushButton, "pushButton_applyDefaultSettings")
        self.button_set_defaults.clicked.connect(self.setDefaults)

        ### Subtype combobox, for now only simple available
        self.subtype_box = self.findChild(
            QComboBox, "comboBox_subtype")

        self.subtype_box.currentIndexChanged.connect(self.subtypeChanged)

        for i in [1,2,3]:
            self.subtype_box.model().item(i).setEnabled(False)

        ### Shape combobox, for now only simple available
        self.shape_box = self.findChild(
            QComboBox, "comboBox_shape")
        self.diagonal_box = self.findChild(QCheckBox, "checkBox_diagonal")

        self.shape_box.currentIndexChanged.connect(self.shapeChanged)
        self.diagonal_box.stateChanged.connect(self.shapeChanged)

        ### Clearence Spinbox
        self.clearence_box = self.findChild(QSpinBox, "spinBox_clearence")
        self.clearence_box.valueChanged.connect(self.clearenceChanged)

        ### Curser combobox
        self.cursor_box = self.findChild(QComboBox, "comboBox_cursor")

        for cursor in cts.cursors:
            self.cursor_box.addItem(cursor.replace('_', ' '))


        ### Names
        self.author_field = self.findChild(QLineEdit, "lineEdit_author")
        self.author_id_field = self.findChild(QLineEdit, "lineEdit_authorID")
        self.object_id_field = self.findChild(QLineEdit, "lineEdit_objectID")
        self.object_original_id_field = self.findChild(QLineEdit, "lineEdit_originalID")
        self.object_name_field = self.findChild(QLineEdit, "lineEdit_objectName")
        self.object_name_lang_field = self.findChild(QLineEdit, "lineEdit_nameInput")

        self.name_lang_box = self.findChild(QComboBox, "comboBox_languageSelect")
        self.name_lang_box.currentIndexChanged.connect(self.languageChanged)
        self.language_index = 0

        self.button_clear_all_languages = self.findChild(QPushButton, "pushButton_clearAllLang")
        self.button_clear_all_languages.clicked.connect(self.clearAllLanguages)

        self.author_field.textEdited.connect(self.authorChanged)
        self.author_id_field.textEdited.connect(self.authorIdChanged)
        self.object_id_field.textEdited.connect(self.idChanged)
        self.object_name_field.textEdited.connect(self.nameChanged)
        self.object_name_lang_field.textEdited.connect(self.nameChangedLang)

        ### Flags
        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.stateChanged.connect(lambda x, flag=checkbox.objectName(): self.flagChanged(x,flag))
        checkbox = self.findChild(QCheckBox, 'isTree')
        checkbox.stateChanged.connect(lambda x, flag=checkbox.objectName(): self.flagChanged(x,flag))
        checkbox = self.findChild(QCheckBox, 'hasTertiaryColour')
        checkbox.stateChanged.connect(lambda x, flag=checkbox.objectName(): self.flagChanged(x,flag))

        ### Spinboxes
        self.spinbox_price = self.findChild(QDoubleSpinBox, "doubleSpinBox_price")
        self.spinbox_removal_price = self.findChild(QDoubleSpinBox, "doubleSpinBox_removalPrice")
        self.spinbox_version = self.findChild(QDoubleSpinBox, "doubleSpinBox_version")

        self.spinbox_price.valueChanged.connect(lambda value, name = 'price': self.spinBoxChanged(value, name))
        self.spinbox_removal_price.valueChanged.connect(lambda value, name = 'removalPrice': self.spinBoxChanged(value, name))
        self.spinbox_version.valueChanged.connect(lambda value, name = 'version': self.spinBoxChanged(value, name))

        checkbox = self.findChild(QCheckBox, 'checkBox_remapCheck')
        checkbox.stateChanged.connect(self.flagRemapChanged)

        self.checkbox_keep_dat_id = self.findChild(QCheckBox, "checkBox_keepOrginalId")

        self.loadObjectSettings(author = author, author_id = author_id)


    def tabChanged(self, index):
        if index == 0:
            self.object_name_field.setText(self.o['strings']['name']['en-GB'])
        elif index == 2 and self.language_index == 0:
            self.object_name_lang_field.setText(self.o['strings']['name']['en-GB'])


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
            self.o['strings']['name'][lang] = ''
        self.object_name_field.setText('')
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
        self.object_name_lang_field.setText(self.o['strings']['name'].get(lang,''))

    def flagChanged(self, value, flag):
        self.o.changeFlag(flag, bool(value))

        self.sprites_tab.updateMainView()

    def flagRemapChanged(self, value):
        self.hasPrimaryColour.setEnabled(not bool(value))
        self.hasSecondaryColour.setEnabled(not bool(value))
        self.hasTertiaryColour.setEnabled(not bool(value))


    def loadObjectSettings(self, author = None, author_id = None):

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
        checkbox.setChecked(self.o['properties'].get('hasTertiaryColour', False))

        self.cursor_box.setCurrentIndex(cts.cursors.index(self.o['properties'].get('cursor','CURSOR_BLANK')))

        if not author:
            author = self.o.data.get('authors','')
            if isinstance(author, list):
                author = ', '.join(author)

        self.author_field.setText(author)
        self.author_id_field.setText(author_id)

        obj_id = self.o.data.get('id', False)
        if obj_id:
            if len(obj_id.split('.')) > 2:
                self.author_id_field.setText(obj_id.split('.')[0])
                self.object_id_field.setText(obj_id.split('.',2)[2])
            else:
                self.object_id_field.setText(obj_id)

        dat_id = self.o.data.get('originalId',False)
        if dat_id:
            self.object_original_id_field.setText(dat_id.split('|')[1].replace(' ', ''))

        self.object_name_field.setText(self.o['strings']['name'].get('en-GB',''))
        self.object_name_lang_field.setText(self.o['strings']['name'].get('en-GB',''))

        self.spinbox_price.setValue(self.o['properties'].get('price', 1))
        self.spinbox_removal_price.setValue(self.o['properties'].get('removalPrice', 1))
        self.spinbox_version.setValue(float(self.o.data.get('version',1.0)))

    def setDefaults(self):

        settings_SS = self.main_window.settings['small_scenery_defaults']

        for flag in settings_SS:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(settings_SS.get(flag, False))

        self.spinbox_price.setValue(settings_SS.get('price', 1))
        self.spinbox_removal_price.setValue(settings_SS.get('removalPrice', 1))
        self.spinbox_version.setValue(settings_SS.get('version',1.0))

        self.cursor_box.setCurrentIndex(cts.cursors.index(settings_SS.get('cursor','CURSOR_BLANK')))


class SpritesTabSS(QWidget):
    def __init__(self, o, object_tab):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/spritesSS.ui'), self)

        self.o = o
        self.object_tab = object_tab
        self.main_window = object_tab.main_window

        main_widget = self.findChild(QGroupBox, "groupBox_spriteSS")

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
        self.button_bounding_box =  self.findChild(
            QToolButton, "toolButton_boundingBox")
        self.button_symm_axes =  self.findChild(
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
        icon.loadFromData(get_data("customwidgets", f'res/icon_reflectionLR.png'), 'png')
        self.button_sprite_left_right.setIcon(QtGui.QIcon(icon))

        icon = QtGui.QPixmap()
        icon.loadFromData(get_data("customwidgets", f'res/icon_reflectionUD.png'), 'png')
        self.button_sprite_up_down.setIcon(QtGui.QIcon(icon))


        self.button_cycle_rotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")

        self.button_cycle_rotation.clicked.connect(self.cycleRotation)

        self.sprite_view_main.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sprite_view_main.customContextMenuRequested.connect(self.showSpriteMenu)


        self.offset = 16 if (self.o.shape == obj.SmallScenery.Shape.QUARTER or self.o.shape == obj.SmallScenery.Shape.QUARTERD) else 32
        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1, self.sprite_view_preview2, self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent = (lambda e, rot=rot: self.previewClicked(rot))
            self.updatePreview(rot)


        # Remap Color Panel
        group_remap = self.findChild(QGroupBox, 'groupBox_remap')
        coords_group = (group_remap.x(),group_remap.y())

        self.button_first_remap = self.findChild(QPushButton, 'pushButton_firstRemap')
        self.select_panel_first_remap = RemapColorSelectWidget(pal.orct, main_widget, self.clickChangeRemap, "1st Remap", self.button_first_remap)
        self.select_panel_first_remap.setGeometry(coords_group[0] + self.button_first_remap.x(), coords_group[1] +  self.button_first_remap.y()-50, 104, 52)
        self.select_panel_first_remap.hide()
        self.button_first_remap.clicked.connect(lambda x, panel_index = 0: self.clickRemapButton(panel_index = panel_index))

        self.button_second_remap = self.findChild(QPushButton, 'pushButton_secondRemap')
        self.select_panel_second_remap = RemapColorSelectWidget(pal.orct, main_widget, self.clickChangeRemap, "2nd Remap", self.button_second_remap)
        self.select_panel_second_remap.setGeometry(coords_group[0] + self.button_second_remap.x(), coords_group[1] +  self.button_second_remap.y()-50, 104, 52)
        self.select_panel_second_remap.hide()
        self.button_second_remap.clicked.connect(lambda x, panel_index = 1: self.clickRemapButton(panel_index = panel_index))

        self.button_third_remap = self.findChild(QPushButton, 'pushButton_thirdRemap')
        self.select_panel_third_remap = RemapColorSelectWidget(pal.orct, main_widget, self.clickChangeRemap, "3rd Remap", self.button_third_remap)
        self.select_panel_third_remap.setGeometry(coords_group[0] + self.button_third_remap.x(), coords_group[1] +  self.button_third_remap.y()-50, 104, 52)
        self.select_panel_third_remap.hide()
        self.button_third_remap.clicked.connect(lambda x, panel_index = 2: self.clickRemapButton(panel_index = panel_index))

        self.select_panels_remap = [self.select_panel_first_remap, self.select_panel_second_remap, self.select_panel_third_remap]
        self.previewClicked(0)


    def loadImage(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            sprite = spr.Sprite.fromFile(filepath, palette = self.main_window.current_palette, use_transparency = True, transparent_color = self.main_window.current_import_color)
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
        submenu_copy.addAction(f"View {(rot + 1 )%4+1}", lambda view = (rot +1)%4: self.copySpriteToView(view))
        submenu_copy.addAction(f"View {(rot + 2 )%4+1}", lambda view = (rot +2)%4: self.copySpriteToView(view))
        submenu_copy.addAction(f"View {(rot + 3 )%4+1}", lambda view = (rot +3)%4: self.copySpriteToView(view))
        submenu_copy.addAction("All Views", self.copySpriteToAllViews)


        menu.addMenu(submenu_copy)


        menu.addAction("Delete Sprite", self.deleteSprite)

        menu.exec_(self.sprite_view_main.mapToGlobal(pos))

    def pasteSpriteFromClipboard(self):
        image = ImageGrab.grabclipboard()

        if image:
            sprite = spr.Sprite(image, palette = self.main_window.current_palette, use_transparency = True, transparent_color = self.main_window.current_import_color)
            self.o.setSprite(sprite)

        self.updateMainView()

    def copySpriteToClipboard(self):
        sprite = self.o.giveSprite()

        image = ImageQt(sprite.image)
        pixmap = QtGui.QPixmap.fromImage(image)

        QApplication.clipboard().setPixmap(pixmap)

    def copySpriteToView(self, view):
        self.o.setSprite(self.o.giveSprite(), rotation = view)

        self.updatePreview(view)

    def copySpriteToAllViews(self):
        rot = self.o.rotation

        for view in range(3):
            self.o.setSprite(self.o.giveSprite(), rotation = (rot + view + 1)% 4 )

        self.updateAllViews()

    def deleteSprite(self):
        sprite = spr.Sprite(None, palette = self.main_window.current_palette)
        self.o.setSprite(sprite)

        self.updateMainView()


    def cycleRotation(self):
        self.o.cycleSpritesRotation()
        for rot in range(4):
            self.updatePreview(rot)

        self.updateMainView()

    def previewClicked(self, rot):
        old_rot = self.o.rotation
        self.sprite_preview[old_rot].setStyleSheet("background-color :  black; border:2px outset black;")
        self.sprite_preview[rot].setStyleSheet("background-color :  black; border:2px outset green;")

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



    def clickChangeRemap(self, color, remap, button, shade):
        self.o.changeRemap(color, remap)

        if shade:
            button.setStyleSheet("QPushButton"
                                 "{"
                                 f"background-color :  rgb{shade};"
                                 "}")
        else:
            button.setStyleSheet("")

        self.updateAllViews()


    def updateMainView(self):
        im, x, y = self.o.show()

        coords = (76+x, 200+y)

        canvas = Image.new('RGBA', (152, 271))

        if self.button_bounding_box.isChecked():
            backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(self.o)
            canvas.paste(backbox, (76+coords_backbox[0], 200+coords_backbox[1]), backbox)

        canvas.paste(im, coords, im)

        if self.button_symm_axes.isChecked():
            symm_axis, coords_symm_axis = self.main_window.symm_axes.giveSymmAxes(self.o)
            canvas.paste(symm_axis, (76+coords_symm_axis[0], 200+coords_symm_axis[1]), symm_axis)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main.setPixmap(pixmap)

        if self.object_tab.locked:
            self.object_tab.locked_sprite_tab.updateView(skip_locked = True)

        self.updatePreview(self.o.rotation)

    def giveMainView(self, canvas_size, add_auxiliaries):
        im, x, y = self.o.show()


        canvas = Image.new('RGBA', (canvas_size, canvas_size))

        if add_auxiliaries and self.button_bounding_box.isChecked():
            backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(self.o)
            canvas.paste(backbox, (int(canvas_size/2)+coords_backbox[0], int(canvas_size*2/3)+coords_backbox[1]), backbox)

        coords = (int(canvas_size/2)+x, int(canvas_size*2/3)+y)

        canvas.paste(im, coords, im)

        if add_auxiliaries and self.button_symm_axes.isChecked():
            symm_axis, coords_symm_axis = self.main_window.symm_axes.giveSymmAxes(self.o)
            canvas.paste(symm_axis, (int(canvas_size/2)+coords_symm_axis[0], int(canvas_size*2/3)+coords_symm_axis[1]), symm_axis)


        return canvas

    def updatePreview(self,rot):
        im, x, y = self.o.show(rotation = rot)
        im = copy(im)
        im.thumbnail((72, 72), Image.NEAREST)
        coords = (int(34-im.size[0]/2),int(36-im.size[1]/2))

        canvas = Image.new('RGBA', (72, 72))
        canvas.paste(im, coords, im)
        #canvas.paste(self.frame_image, self.frame_image)
        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)

    def updateAllViews(self):
        self.updateMainView()
        for rot in range(4):
            self.updatePreview(rot)

#### Sprites Tab

class SpriteTab(QWidget):
    def __init__(self, main_window, object_tab = None, filepath = None):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/sprite.ui'), self)

        self.main_window = main_window

        self.scroll_area.connectTab(self)
        self.canvas_size = 200

        self.lastpos = (0,0)

        # Sprite zoom
        self.zoom_factor = 1
        self.slider_zoom.valueChanged.connect(self.zoomChanged)
        self.slider_zoom.valueChanged.connect(lambda x, toolbox = self.main_window.toolbox: self.toolChanged(toolbox))


        if object_tab:
            self.locked = True
            self.object_tab = object_tab
            object_tab.lockWithSpriteTab(self)

            self.sprite, _ = object_tab.giveCurrentMainViewSprite()
            o = object_tab.o
            self.history = []
            self.history_redo = []
            for sprite in o.sprites:
                self.history.append([])
                self.history_redo.append([])

        else:
            self.locked = False
            self.object_tab = None
            self.sprite = spr.Sprite(None)
            self.history = [[]]
            self.history_redo = [[]]

        self.protected_pixels = Image.new('1', (self.canvas_size,self.canvas_size))



        self.lastpath = filepath
        self.saved = False
        self.main_window.toolbox.toolChanged.connect(self.toolChanged)
        self.toolChanged(self.main_window.toolbox)

        self.view.mousePressEvent = self.viewMousePressEvent
        self.view.mouseMoveEvent = self.viewMouseMoveEvent
        self.view.wheelEvent = self.viewWheelEvent
        self.view.keyPressEvent = self.viewKeyPressEvent

        self.updateView()

    def lockWithObjectTab(self, object_tab):
        if object_tab:
            self.locked = True
            self.object_tab = object_tab
            self.sprite, _ = object_tab.giveCurrentMainViewSprite()
            o = object_tab.o
            self.history = []
            self.history_redo = []
            for sprite in o.sprites:
                self.history.append([])
                self.history_redo.append([])

        self.updateView()

    def unlockObjectTab(self):
        if self.locked:
            self.sprite = copy(self.giveSprite()[0])
            index = self.giveSprite()[1]
            self.history = copy([self.history[index]])
            self.history_redo = copy([self.history_redo[index]])
            self.locked = False
            self.object_tab = None

    def setSprite(self, sprite):
        self.sprite = copy(sprite)

        self.updateView()

    def zoomChanged(self, val):
        self.zoom_factor = val

        self.updateView()

    def toolChanged(self, toolbox):
        cursor = cwdg.ToolCursors(toolbox, self.zoom_factor)
        self.view.setCursor(cursor)

    def colorRemap(self, color_remap, selected_colors):
        self.addSpriteToHistory()
        sprite, _ = self.giveSprite()

        for color in selected_colors:
            sprite.remapColor(color, color_remap)

        self.updateView()

    def colorChangeBrightness(self, step, selected_colors):
        self.addSpriteToHistory()
        sprite, _ = self.giveSprite()

        sprite.changeBrightnessColor(step, selected_colors)

        self.updateView()

    def colorRemove(self, selected_colors):
        self.addSpriteToHistory()
        sprite, _ = self.giveSprite()

        sprite.removeColor(selected_colors)

        self.updateView()

    def clickSpriteControl(self, direction: str):
        sprite, _ = self.giveSprite()

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

        self.updateView()


    def draw(self, x, y, shade):
        sprite, _ = self.giveSprite()
        canvas = Image.new('RGBA', (self.canvas_size,self.canvas_size))
        canvas_protect = Image.new('RGBA', (self.canvas_size,self.canvas_size))

        coords = (int(self.canvas_size/2)+sprite.x, int(self.canvas_size*2/3)+sprite.y)

        canvas.paste(sprite.image, coords, mask = sprite.image)
        canvas_protect.paste(sprite.image, coords, mask = sprite.image)


        brushsize = self.main_window.giveBrushsize()

        draw = ImageDraw.Draw(canvas)
        if brushsize != 1:
            draw.rectangle([(x,y),(x+brushsize-1,y+brushsize-1)],  fill=shade)
        else:
            draw.point((x,y), shade)

        if self.lastpos != (x,y):
            x0, y0 = self.lastpos
            if brushsize % 2 == 0:
                x_mod = -1 if y > y0 else 0
                y_mod = -1 if x > x0 else 0
            else:
                x_mod = 0
                y_mod = 0

            draw.line([(int(x0+brushsize/2)+x_mod, int(y0+brushsize/2)+y_mod), (int(x+brushsize/2)+x_mod,int(y+brushsize/2)+y_mod)], fill=shade, width=brushsize)

            self.lastpos = (x,y)


        canvas.paste(canvas_protect, mask=self.protected_pixels)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -int(self.canvas_size/2) + bbox[0]
            y_offset = -int(self.canvas_size*2/3) + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        sprite.x = x_offset
        sprite.y = y_offset

        self.updateView()

    def erase(self, x,y):
        self.draw(x,y,(0,0,0,0))

    def eyedrop(self, x,y):
        sprite, _ = self.giveSprite()

        coords = (int(self.canvas_size/2)+sprite.x, int(self.canvas_size*2/3)+sprite.y)

        indices = sprite.giveShade((x-coords[0],y-coords[1]))


        if not indices:
            return

        self.main_window.color_select_panel.setColor(indices[0], indices[1])

    def overdraw(self, x, y):
        working_sprite = self.working_sprite
        sprite, _ = self.giveSprite()
        canvas_mask = Image.new('1', (self.canvas_size,self.canvas_size), color=1)
        canvas = Image.new('RGBA', (self.canvas_size,self.canvas_size))
        canvas_protect = Image.new('RGBA', (self.canvas_size,self.canvas_size))

        coords = (int(self.canvas_size/2)+sprite.x, int(self.canvas_size*2/3)+sprite.y)

        canvas.paste(working_sprite.image, coords, mask = working_sprite.image)
        canvas_protect.paste(sprite.image, coords, mask = sprite.image)

        brushsize = self.main_window.giveBrushsize()

        draw = ImageDraw.Draw(canvas_mask)
        if brushsize != 1:
            draw.rectangle([(x,y),(x+brushsize-1,y+brushsize-1)],  fill=0)
        else:
            draw.point((x,y), 0)

        if self.lastpos != (x,y):
            x0, y0 = self.lastpos
            if brushsize % 2 == 0:
                x_mod = -1 if y > y0 else 0
                y_mod = -1 if x > x0 else 0
            else:
                x_mod = 0
                y_mod = 0

            draw.line([(int(x0+brushsize/2)+x_mod, int(y0+brushsize/2)+y_mod), (int(x+brushsize/2)+x_mod,int(y+brushsize/2)+y_mod)], fill=0, width=brushsize)

            self.lastpos = (x,y)

        canvas_mask.paste(self.protected_pixels, mask = self.protected_pixels)


        canvas.paste(canvas_protect, mask=canvas_mask)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -int(self.canvas_size/2) + bbox[0]
            y_offset = -int(self.canvas_size*2/3) + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        sprite.x = x_offset
        sprite.y = y_offset

        self.updateView()

    def fill(self, x, y, shade):
        sprite, _ = self.giveSprite()
        canvas = Image.new('RGBA', (self.canvas_size,self.canvas_size))
        canvas_protect = Image.new('RGBA', (self.canvas_size,self.canvas_size))

        coords = (int(self.canvas_size/2)+sprite.x, int(self.canvas_size*2/3)+sprite.y)

        canvas.paste(sprite.image, coords, mask = sprite.image)
        canvas_protect.paste(sprite.image, coords, mask = sprite.image)


        ImageDraw.floodfill(canvas, (x,y), (shade[0],shade[1],shade[2],255))

        canvas.paste(canvas_protect, mask=self.protected_pixels)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -int(self.canvas_size/2) + bbox[0]
            y_offset = -int(self.canvas_size*2/3) + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        sprite.x = x_offset
        sprite.y = y_offset

        self.updateView()

    def generateProtectionMask(self):
        sprite, _ = self.giveSprite()

        coords = (int(self.canvas_size/2)+sprite.x, int(self.canvas_size*2/3)+sprite.y)

        self.protected_pixels = Image.new('1', (self.canvas_size,self.canvas_size))
        self.protected_pixels.paste(sprite.giveProtectedPixelMask(self.main_window.color_select_panel.notSelectedColors()), coords)

        if self.main_window.giveBrush() == cwdg.Brushes.AIRBRUSH:
            strength = self.main_window.giveAirbrushStrength()
            noise_mask = Image.fromarray(np.random.choice(a=[True, False], size=(self.canvas_size,self.canvas_size), p=[1-strength, strength]).T)
            self.protected_pixels.paste(noise_mask, mask = noise_mask)


    def viewKeyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Up:
            self.clickSpriteControl('up')


    def viewMousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # Control modifier = sprite control, dealt with by parent
        if modifiers == QtCore.Qt.ControlModifier:
            event.ignore()
            return

        screen_pos = event.localPos()
        x = round(screen_pos.x()/self.zoom_factor)
        y = round(screen_pos.y()/self.zoom_factor)


        self.lastpos = (x,y)


        if event.button() == QtCore.Qt.LeftButton:
            if self.main_window.giveTool() == cwdg.Tools.PEN:

                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.draw(x, y, shade)
                return

            if self.main_window.giveTool() == cwdg.Tools.ERASER:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.EYEDROPPER:

                #since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x()/self.zoom_factor)
                y = int(screen_pos.y()/self.zoom_factor)

                self.eyedrop(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.REMAP:

                color_remap = self.main_window.color_select_panel.getColorIndices()[0]
                if not color_remap:
                    self.working_sprite = None
                    return

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.working_sprite = copy(self.giveSprite()[0])

                for color in self.main_window.color_select_panel.selectedColors():
                    self.working_sprite.remapColor(color, color_remap)

                self.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.working_sprite = copy(self.giveSprite()[0])

                color_remap = self.main_window.color_select_panel.getColorIndices()[0]

                for color in self.main_window.color_select_panel.selectedColors():
                    self.working_sprite.changeBrightnessColor(1,color)

                self.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.FILL:

                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                #since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x()/self.zoom_factor)
                y = int(screen_pos.y()/self.zoom_factor)


                self.addSpriteToHistory()
                self.generateProtectionMask()

                self.fill(x, y, shade)
                return


        if event.button() == QtCore.Qt.RightButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.working_sprite = copy(self.giveSprite()[0])

                color_remap = self.main_window.color_select_panel.getColorIndices()[0]

                for color in self.main_window.color_select_panel.selectedColors():
                    self.working_sprite.changeBrightnessColor(-1,color)

                self.overdraw(x,y)
                return

    def viewMouseMoveEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # Control modifier = sprite control, dealt with by parent
        if modifiers == QtCore.Qt.ControlModifier:
            event.ignore()
            return

        screen_pos = event.localPos()
        x = round(screen_pos.x()/self.zoom_factor)
        y = round(screen_pos.y()/self.zoom_factor)

        if event.buttons() == QtCore.Qt.LeftButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:
                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                self.draw(x,y,shade)
                return

            if self.main_window.giveTool() == cwdg.Tools.ERASER:
                self.erase(x,y)
                return

            if self.main_window.giveTool() == cwdg.Tools.EYEDROPPER:

                #since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x()/self.zoom_factor)
                y = int(screen_pos.y()/self.zoom_factor)

                self.eyedrop(x,y)
                return


            if self.main_window.giveTool() == cwdg.Tools.REMAP:
                if not self.working_sprite:
                    return

                self.overdraw(x,y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:
                if not self.working_sprite:
                    return

                self.overdraw(x,y)
                return

        if event.buttons() == QtCore.Qt.RightButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:
                self.erase(x,y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:
                self.overdraw(x,y)
                return


    def viewWheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.AltModifier:
            color, shade = self.main_window.color_select_panel.getColorIndices()
            if color:
                if event.angleDelta().x() > 0 and shade != 11:
                    self.main_window.color_select_panel.setColor(color, shade+1)
                elif  event.angleDelta().x() < 0 and shade != 0:
                    self.main_window.color_select_panel.setColor(color, shade-1)
        elif modifiers == QtCore.Qt.ShiftModifier:
            toolbox = self.main_window.toolbox
            if event.angleDelta().y() > 0:
                toolbox.dial_brushsize.setValue(toolbox.dial_brushsize.value()+1)
            elif  event.angleDelta().y() < 0:
                toolbox.dial_brushsize.setValue(toolbox.dial_brushsize.value()-1)


    def updateView(self, skip_locked = False):
        if self.locked:
            if not skip_locked:
                self.object_tab.updateCurrentMainView()

                return

            canvas = self.object_tab.giveCurrentMainView(self.canvas_size, add_auxilaries = True)

        else:
            canvas = Image.new('RGBA', (self.canvas_size, self.canvas_size))

            #if add_auxiliaries and self.button_bounding_box.isChecked():
            #    backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(self.o)
            #    canvas.paste(backbox, (int(canvas_size/2)+coords_backbox[0], int(canvas_size*2/3)+coords_backbox[1]), backbox)


            #canvas.paste(self.frame_image, self.frame_image)

            coords = (int(self.canvas_size/2)+self.sprite.x, int(self.canvas_size*2/3)+self.sprite.y)

            canvas.paste(self.sprite.image, coords, self.sprite.image)



        canvas = canvas.resize((int(canvas.size[0]*self.zoom_factor), int(canvas.size[1]*self.zoom_factor)), resample=Image.NEAREST)
        image = ImageQt(canvas)

        pixmap = QtGui.QPixmap.fromImage(image)
        self.view.setPixmap(pixmap)

        geometry = self.scroll_area.geometry()
        scroll_width = max(self.view.size().width(), geometry.width())
        scroll_height = max(self.view.size().height(), geometry.height())

        self.scroll_area_content.resize(scroll_width, scroll_height)

    def giveSprite(self):
        if self.locked:
            return self.object_tab.giveCurrentMainViewSprite()
        else:
            return self.sprite, 0

    def addSpriteToHistory(self):
        sprite_import, index = self.giveSprite()
        sprite = copy(sprite_import)

        if len(self.history[index]) == self.main_window.settings['history_maximum']:
            self.history[index].pop(0)


        self.history[index].append(sprite)
        self.history_redo[index] = []

    def undo(self):
        sprite_old, index = self.giveSprite()

        if len(self.history[index]) == 0:
            return

        sprite_new = self.history[index].pop(-1)

        self.history_redo[index].append(copy(sprite_old))

        sprite_old.image = sprite_new.image
        sprite_old.x = sprite_new.x
        sprite_old.y = sprite_new.y

        self.updateView()

    def redo(self):
        sprite_old, index = self.giveSprite()

        if len(self.history_redo[index]) == 0:
            return

        sprite_new = self.history_redo[index].pop(-1)

        self.history[index].append(copy(sprite_old))


        sprite_old.image = sprite_new.image
        sprite_old.x = sprite_new.x
        sprite_old.y = sprite_new.y

        self.updateView()

    def paste(self):
        if self.locked:
            self.object_tab.sprites_tab.pasteSpriteFromClipboard()
        else:
            pass

    def copy(self):
        if self.locked:
            self.object_tab.sprites_tab.copySpriteToClipboard()
        else:
            pass




class SpriteViewWidget(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tab = None

        self.slider_zoom = None
        self.current_pressed_key = None
        self.mousepos = QtCore.QPoint(0, 0)

        self.setVerticalScrollBar(self.KeepPositionScrollBar(QtCore.Qt.Vertical, self))
        self.setHorizontalScrollBar(self.KeepPositionScrollBar(QtCore.Qt.Horizontal, self))


    def connectTab(self,tab):
        self.tab = tab
        self.slider_zoom = tab.slider_zoom


    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        #we ignore the event when Alt is pressed as it is the color change movement
        if modifiers == QtCore.Qt.ShiftModifier or modifiers == QtCore.Qt.AltModifier:
            return

        if not self.slider_zoom:
            super().wheelEvent()
            return

        if modifiers == QtCore.Qt.ControlModifier:
            zoom_factor = self.slider_zoom.value()
            if event.angleDelta().y() > 0 and zoom_factor != self.slider_zoom.maximum():
                self.slider_zoom.setValue(int(zoom_factor+1))
            elif  event.angleDelta().y() < 0 and zoom_factor != self.slider_zoom.minimum():
                self.slider_zoom.setValue(int(zoom_factor-1))
        else:
            super().wheelEvent(event)


    def mousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if event.button() == QtCore.Qt.LeftButton and modifiers == QtCore.Qt.ControlModifier:
            QApplication.setOverrideCursor(QtCore.Qt.ClosedHandCursor)
            self.mousepos = event.localPos()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # Skip scrolling when Ctrl is pressed (Colorselect)
        if modifiers == QtCore.Qt.AltModifier:
            event.ignore()
            return


        delta = event.localPos() - self.mousepos

        # panning area
        if event.buttons() == QtCore.Qt.LeftButton and modifiers == QtCore.Qt.ControlModifier:
            h = self.horizontalScrollBar().value()
            v = self.verticalScrollBar().value()

            self.horizontalScrollBar().setValue(int(h - delta.x()))
            self.verticalScrollBar().setValue(int(v - delta.y()))

        self.mousepos = event.localPos()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        self.mousepos = event.localPos()
        super().mouseReleaseEvent(event)


    class KeepPositionScrollBar(QScrollBar):
        defaultRatio = .5
        ratio = .5
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.rangeChanged.connect(self.restoreRatio)
            self.valueChanged.connect(self.updateRatio)

        def restoreRatio(self):
            absValue = (self.maximum() - self.minimum()) * self.ratio
            self.setValue(round(self.minimum() + absValue))

        def updateRatio(self):
            if self.maximum() - self.minimum():
                absValue = self.value() - self.minimum()
                self.ratio = absValue / (self.maximum() - self.minimum())
            else:
                self.ratio = self.defaultRatio



##### Settings window

class ChangeSettingsUi(QDialog):
    def __init__(self, settings):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/settings_window.ui'), self)

        self.setFixedSize(self.size())

        self.lineEdit_openpath.setText(settings.get('openpath'))
        self.lineEdit_saveDefault.setText(settings.get('savedefault'))
        self.lineEdit_openDefault.setText(settings.get('opendefault'))

        self.lineEdit_authorID.setText(settings.get('author_id'))
        self.lineEdit_author.setText(settings.get('author'))

        self.pushButton_changeOpenpath.clicked.connect(lambda x, sender = self.lineEdit_openpath:
            self.clickChangeFolder(sender))
        self.pushButton_changeSaveDefault.clicked.connect(lambda x, sender = self.lineEdit_saveDefault:
            self.clickChangeFolder(sender))
        self.pushButton_changeOpenDefault.clicked.connect(lambda x, sender = self.lineEdit_openDefault:
            self.clickChangeFolder(sender))

        self.checkBox_nozip.setChecked(settings.get('no_zip', False))
        self.comboBox_transparencycolor.setCurrentIndex(settings.get('transparency_color', 0))
        self.spinBox_R.setValue(settings.get('import_color', (0,0,0))[0])
        self.spinBox_G.setValue(settings.get('import_color', (0,0,0))[1])
        self.spinBox_B.setValue(settings.get('import_color', (0,0,0))[2])
        self.doubleSpinBox_version.setValue(float(settings.get('version', 1)))

        self.comboBox_palette.setCurrentIndex(settings.get('palette', 0))
        self.spinBox_history_maximum.setValue(settings.get('history_maximum', 5))


        self.loadSSSettings(settings)


    def loadSSSettings(self, settings):
        for flag in cts.Jsmall_flags:
            checkbox = self.tab_SS_default.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(settings.get('small_scenery_defaults',{}).get(flag, False))

        checkbox = self.tab_SS_default.findChild(QCheckBox, 'isTree')
        checkbox.setChecked(settings.get('small_scenery_defaults',{}).get('isTree', False))

        self.cursor_box = self.tab_SS_default.findChild(QComboBox, "comboBox_cursor")

        for cursor in cts.cursors:
            self.cursor_box.addItem(cursor.replace('_', ' '))

        self.cursor_box.setCurrentText(settings.get('small_scenery_defaults',{}).get('cursor', 'CURSOR BLANK'))

        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_price")
        spinbox.setValue(int(settings.get('small_scenery_defaults',{}).get('price', 1)))
        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_removalPrice")
        spinbox.setValue(int(settings.get('small_scenery_defaults',{}).get('removalPrice', 1)))




    def clickChangeFolder(self, sender):

        directory = sender.text() if sender.text() != '' else "%USERPROFILE%/Documents/"
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", directory = directory)
        if folder:
            sender.setText(folder)


    def retrieveInputs(self):
        settings = {}

        settings['openpath'] = self.lineEdit_openpath.text()
        settings['savedefault'] =self.lineEdit_saveDefault.text()
        settings['opendefault'] =self.lineEdit_openDefault.text()
        settings['author'] = self.lineEdit_author.text()
        settings['author_id'] = self.lineEdit_authorID.text()
        settings['no_zip'] = self.checkBox_nozip.isChecked()
        settings['version'] = self.doubleSpinBox_version.value()
        settings['transparency_color'] = self.comboBox_transparencycolor.currentIndex()
        settings['import_color'] = [self.spinBox_R.value(),self.spinBox_G.value(),self.spinBox_B.value()]
        settings['palette'] = self.comboBox_palette.currentIndex()
        settings['history_maximum'] = self.spinBox_history_maximum.value()


        ss_defaults = {}
        for flag in cts.Jsmall_flags:
            checkbox = self.tab_SS_default.findChild(QCheckBox, flag)
            if checkbox:
                ss_defaults[flag] = checkbox.isChecked()

        ss_defaults['isTree'] = self.isTree.isChecked()

        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_price")
        ss_defaults['price'] = spinbox.value()
        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_removalPrice")
        ss_defaults['removalPrice'] = spinbox.value()

        ss_defaults['cursor'] = self.tab_SS_default.findChild(QComboBox, "comboBox_cursor").currentText().replace(' ', '_')

        settings['small_scenery_defaults'] = ss_defaults

        return settings

    def accept(self):

         self.ret = self.retrieveInputs()
         super().accept()















