# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2024 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QSlider, QTableWidgetItem
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
        super().__init__(o, object_tab, sprites_tab)

        uic.loadUi(aux.resource_path('gui/settingsSS.ui'), self)

        self.tab_widget = self.findChild(QTabWidget, "tabWidget_settingsSS")
        self.tab_widget.currentChanged.connect(self.tabChanged)

        super().initializeWidgets()

        self.button_set_defaults = self.findChild(
            QPushButton, "pushButton_applyDefaultSettings")
        self.button_set_defaults.clicked.connect(self.setDefaults)

        # Subtype combobox
        self.subtype_box = self.findChild(
            QComboBox, "comboBox_subtype")

        self.subtype_box.currentIndexChanged.connect(self.subtypeChanged)

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

        self.cursor_box.currentIndexChanged.connect(self.cursorChanged)

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

        # Animation
        self.animation_widget = self.findChild(
            QGroupBox, 'groupBox_animOptions')

        self.button_animation_sequence = self.findChild(
            QPushButton, 'pushButton_editAnimSequence')
        self.button_animation_sequence.clicked.connect(
            self.clickAnimationSequence)

        # Animationsubtype combobox
        self.anim_subtype_box = self.findChild(
            QComboBox, "comboBox_animSubtype")

        self.anim_subtype_box.currentIndexChanged.connect(
            self.animationTypeChanged)

        # Animation Spinboxes
        self.spinbox_frame_delay = self.findChild(
            QSpinBox, "spinBox_frameDelay")
        self.spinbox_anim_delay = self.findChild(
            QSpinBox, "spinBox_animDelay")
        self.spinbox_anim_num_image_sets = self.findChild(
            QSpinBox, "spinBox_numSprites")

        self.spinbox_frame_delay.valueChanged.connect(
            lambda value, name='animationDelay': self.spinBoxChanged(value, name))
        self.spinbox_anim_delay.valueChanged.connect(
            self.animationDelayChanged)
        self.spinbox_anim_num_image_sets.valueChanged.connect(
            self.animationNumImageSetsChanged)

        checkbox = self.findChild(
            QCheckBox, 'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED')
        checkbox.stateChanged.connect(self.animationChangePreviewImage)
        checkbox = self.findChild(QCheckBox, 'SMALL_SCENERY_FLAG17')
        checkbox.stateChanged.connect(self.animationChangePreviewImage)

        self.loadObjectSettings(author=author, author_id=author_id)

    def giveDummy(self):
        dummy_o = obj.newEmpty(obj.Type.SMALL)
        dummy_o.changeShape(self.o.shape)
        dummy_o['properties']['height'] = int(self.o['properties']['height'])
        dummy_o.rotation = int(self.o.rotation)

        return dummy_o

    def subtypeChanged(self, value):
        value = self.subtype_box.currentIndex()

        subtype = list(obj.SmallScenery.Subtype)[value]

        self.o.changeSubtype(subtype)

        self.sprites_tab.widget_frame_controls.setEnabled(
            subtype == obj.SmallScenery.Subtype.GARDENS or subtype == obj.SmallScenery.Subtype.ANIMATED)
        self.sprites_tab.widget_animation_controls.setEnabled(
            subtype == obj.SmallScenery.Subtype.ANIMATED)

        self.animation_widget.setEnabled(
            subtype == obj.SmallScenery.Subtype.ANIMATED)

        if subtype == obj.SmallScenery.Subtype.GARDENS:
            self.sprites_tab.slider_sprite_index.setMaximum(2)
            self.sprites_tab.spinbox_sprite_index.setMaximum(2)
        elif subtype == obj.SmallScenery.Subtype.ANIMATED:
            self.sprites_tab.slider_sprite_index.setMaximum(
                self.o.num_image_sets-1+int(self.o.has_preview))
            self.sprites_tab.spinbox_sprite_index.setMaximum(
                self.o.num_image_sets-1+int(self.o.has_preview))
            self.animation_widget.setEnabled(True)

            self.anim_subtype_box.setCurrentIndex(self.o.animation_type.value)
        else:
            self.sprites_tab.slider_sprite_index.setMaximum(0)
            self.sprites_tab.spinbox_sprite_index.setMaximum(0)

        self.loadObjectSettings()
        self.sprites_tab.updateLockedSpriteLayersModel()
        self.sprites_tab.updateAllViews()

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

    def cursorChanged(self):
        value = self.cursor_box.currentIndex()

        self.o['properties']['cursor'] = cts.cursors[value]

    def authorChanged(self, value):
        self.o['authors'] = [name.strip() for name in value.split(',')]

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

    def clickAnimationSequence(self):
        dialog = EditAnimationSequenceUI(self.o)

        if dialog.exec():
            self.o['properties']['frameOffsets'] = dialog.sequence
            self.o['properties']['numFrames'] = len(dialog.sequence)
            self.o['properties']['animationMask'] = len(
                dialog.sequence) * 2**self.spinbox_anim_delay.value() - 1
            self.spinbox_anim_num_image_sets.setValue(dialog.num_image_sets)

    def animationTypeChanged(self, value):
        value = self.anim_subtype_box.currentIndex()

        anim_type = list(obj.SmallScenery.AnimationType)[value]

        self.o.changeAnimationType(anim_type)

        self.container_anim.setEnabled(
            self.o.animation_type == self.o.AnimationType.REGULAR)

        self.spinbox_anim_num_image_sets.setValue(self.o.num_image_sets)

        if anim_type == obj.SmallScenery.AnimationType.REGULAR:
            self.spinbox_frame_delay.setValue(
                self.o['properties'].get('animationDelay', 0))
            length = self.o['properties'].get('animationMask', 0)
            num_frames = self.o['properties'].get('numFrames', 1)

            delay = int(np.log2((length+1)/num_frames))

            self.spinbox_anim_delay.setValue(delay)

        self.sprites_tab.updateLockedSpriteLayersModel()

    def animationDelayChanged(self, value):
        num_frames = self.o['properties'].get('numFrames', False)

        if num_frames:
            self.o['properties']['animationMask'] = num_frames * 2**value - 1

    def animationNumImageSetsChanged(self, value):
        self.sprites_tab.slider_sprite_index.setMaximum(
            value-1+int(self.o.has_preview))
        self.sprites_tab.spinbox_sprite_index.setMaximum(
            value-1+int(self.o.has_preview))
        if self.o.num_image_sets == value:
            return

        self.o.changeNumImagesSets(value)

        self.sprites_tab.updateLockedSpriteLayersModel()

    def animationChangePreviewImage(self):
        self.o.updateAnimPreviewImage()

        self.sprites_tab.slider_sprite_index.setMaximum(
            self.o.num_image_sets-1+int(self.o.has_preview))
        self.sprites_tab.spinbox_sprite_index.setMaximum(
            self.o.num_image_sets-1+int(self.o.has_preview))

        self.sprites_tab.updateLockedSpriteLayersModel()

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

        self.scenery_group_id_field.setText(
            self.o['properties'].get('sceneryGroup', ''))
        self.mirror_object_id_field.setText(
            self.o['properties'].get('mirrorObjectId', ''))

        self.spinbox_price.setValue(self.o['properties'].get('price', 1))
        self.spinbox_removal_price.setValue(
            self.o['properties'].get('removalPrice', 1))
        self.spinbox_version.setValue(float(self.o.data.get('version', 1.0)))

        if self.o['properties'].get('isAnimated'):
            self.animation_widget.setEnabled(True)

            self.anim_subtype_box.setCurrentIndex(self.o.animation_type.value)
            if self.o.animation_type == obj.SmallScenery.AnimationType.REGULAR:
                self.spinbox_anim_num_image_sets.setValue(
                    self.o.num_image_sets)
                self.spinbox_frame_delay.setValue(
                    self.o['properties'].get('animationDelay', 0))
                num_frames = self.o['properties'].get('numFrames')
                self.spinbox_anim_delay.setValue(int(
                    np.log2((self.o['properties']['animationMask'] + 1)/num_frames)))

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


class SpritesTab(widgetsGeneric.SpritesTabAll):
    def __init__(self, o, object_tab):
        super().__init__(o, object_tab)
        uic.loadUi(aux.resource_path('gui/spritesSS.ui'), self)

        self.initializeWidgets(151, 268)

        self.button_cycle_animation_frame = self.findChild(
            QPushButton, "pushButton_cycleFrame")

        self.button_cycle_animation_frame.clicked.connect(
            self.cycleAnimationFrame)

        self.slider_sprite_index = self.findChild(
            QSlider, "horizontalSlider_spriteIndex")
        self.slider_sprite_index.valueChanged.connect(
            self.updateLockedSpriteLayersModel)

        self.widget_frame_controls = self.findChild(
            QWidget, "groupBox_frame_controls")
        self.widget_frame_controls.setEnabled(False)

        self.previewClicked(0)
        self.updateAllViews()

    def cycleAnimationFrame(self):
        view = -1 if self.checkBox_allViewsCycleFrame.isChecked() else self.o.rotation

        self.o.cycleAnimationFrame(view=view)

        self.updateLockedSpriteLayersModel()
        self.updateAllViews()

    def createLayers(self):
        self.layers = [[], [], [], []]

        if self.o.subtype == obj.SmallScenery.Subtype.GLASS:
            for rot in range(4):
                sprite = self.o.giveSprite(rotation=rot)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, 0, 0, 0, 0, name=f'Structure View {rot+1}', locked_id=0)
                self.layers[rot].append(layer)
            for rot in range(4):
                sprite = self.o.giveSprite(rotation=rot, glass=True)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, 0, 0, 0, 0, name=f'Glass View {rot+1}', locked_id=1)
                self.layers[rot].append(layer)
        elif self.o.subtype == obj.SmallScenery.Subtype.GARDENS:
            if self.slider_sprite_index.value() == 0:
                for rot in range(4):
                    sprite = self.o.giveSprite(rotation=rot, wither=0)
                    layer = wdg.SpriteLayer(
                        sprite, self.main_window, 0, 0, 0, 0, name=f'Watered View {rot+1}')
                    self.layers[rot].append(layer)
            elif self.slider_sprite_index.value() == 1:
                for rot in range(4):
                    sprite = self.o.giveSprite(rotation=rot, wither=1)
                    layer = wdg.SpriteLayer(
                        sprite, self.main_window, 0, 0, 0, 0, name=f'Wither 1 View {rot+1}')
                    self.layers[rot].append(layer)
            elif self.slider_sprite_index.value() == 2:
                for rot in range(4):
                    sprite = self.o.giveSprite(rotation=rot, wither=2)
                    layer = wdg.SpriteLayer(
                        sprite, self.main_window, 0, 0, 0, 0, name=f'Wither 2 View {rot+1}')
                    self.layers[rot].append(layer)
        elif self.o.subtype == obj.SmallScenery.Subtype.ANIMATED:
            animation_frame = self.slider_sprite_index.value()
            if self.o.animation_type in [
                    obj.SmallScenery.AnimationType.FOUNTAIN1, obj.SmallScenery.AnimationType.FOUNTAIN4]:
                for rot in range(4):
                    base_index = rot
                    fountain_index = rot+4*(animation_frame+1)
                    fountain_index += 4 if self.o.animation_type == obj.SmallScenery.AnimationType.FOUNTAIN4 else 0

                    sprite = self.o.sprites[self.o.data['images']
                                            [base_index]['path']]
                    layer = wdg.SpriteLayer(
                        sprite, self.main_window, 0, 0, 0, 0, name=f'Base 1 View {rot+1}', locked_id=0)
                    self.layers[rot].append(layer)

                    sprite = self.o.sprites[self.o.data['images']
                                            [fountain_index]['path']]
                    layer = wdg.SpriteLayer(
                        sprite, self.main_window, 0, 0, 0, 0,
                        name=f'Jets 1 Animation Frame {animation_frame + 1} View {rot+1}', locked_id=1)
                    self.layers[rot].append(layer)

                    if self.o.animation_type == obj.SmallScenery.AnimationType.FOUNTAIN4:
                        sprite = self.o.sprites[self.o.data['images']
                                                [base_index+4]['path']]
                        layer = wdg.SpriteLayer(
                            sprite, self.main_window, 0, 0, 0, 0, name=f'Base 2 View {rot+1}', locked_id=2)
                        self.layers[rot].append(layer)
                        sprite = self.o.sprites[self.o.data['images']
                                                [fountain_index+16]['path']]
                        layer = wdg.SpriteLayer(
                            sprite, self.main_window, 0, 0, 0, 0,
                            name=f'Jets 2 Animation Frame {animation_frame + 1} View {rot+1}', locked_id=3)
                        self.layers[rot].append(layer)
            else:
                if animation_frame == 0 and self.o.has_preview:
                    for rot in range(4):
                        sprite = self.o.giveSprite(
                            rotation=rot, animation_frame=animation_frame)
                        layer = wdg.SpriteLayer(
                            sprite, self.main_window, 0, 0, 0, 0, name=f'Preview Image View {rot+1}')
                        self.layers[rot].append(layer)
                else:
                    for rot in range(4):
                        sprite = self.o.giveSprite(
                            rotation=rot, animation_frame=animation_frame)

                        layer = wdg.SpriteLayer(
                            sprite, self.main_window, 0, 0, 0, 0,
                            name=f'Animation Frame {animation_frame + 1 - int(self.o.has_preview)} View {rot+1}')
                        self.layers[rot].append(layer)
        else:
            for rot in range(4):
                sprite = self.o.giveSprite(rotation=rot)
                layer = wdg.SpriteLayer(
                    sprite, self.main_window, 0, 0, 0, 0, name=f'View {rot+1}')
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

    def setCurrentLayers(self, layers, index=0, view=None):
        if view == None:
            view = self.o.rotation

        if self.requestNumberOfLayers() != layers.rowCount():
            dialog = SpriteImportUi(layers, index, self.layers[view])

            if dialog.exec():
                target_index = dialog.selected_index
                layers_incoming = dialog.selected_incoming

                if len(layers_incoming) == 0:
                    return

                layer_top = wdg.SpriteLayer.fromLayer(layers_incoming[0])
                for i in range(len(layers_incoming)-1):
                    layer_bottom = wdg.SpriteLayer.fromLayer(
                        layers_incoming[i+1])
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
        if self.o.subtype == obj.SmallScenery.Subtype.GARDENS:
            im, x, y = self.o.show(wither=self.slider_sprite_index.value())
        elif self.o.subtype == obj.SmallScenery.Subtype.ANIMATED:
            im, x, y = self.o.show(
                animation_frame=self.slider_sprite_index.value())
        else:
            im, x, y = self.o.show()

        height = -y + 90 if -y > 178 else 268
        self.sprite_view_main_scene.setSceneRect(0, 0, 151, height)

        coords = (76+x, height-70+y)

        image = ImageQt(im)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main_item.setOffset(coords[0], coords[1])

        self.sprite_view_main_item.setPixmap(pixmap)

        self.updatePreview(self.o.rotation)
        if emit_signal:
            self.object_tab.mainViewUpdated.emit()

    def updatePreview(self, rot):
        if self.o.subtype == obj.SmallScenery.Subtype.GARDENS:
            im, x, y = self.o.show(
                rotation=rot, wither=self.slider_sprite_index.value())
        elif self.o.subtype == obj.SmallScenery.Subtype.ANIMATED:
            im, x, y = self.o.show(
                rotation=rot, animation_frame=self.slider_sprite_index.value())
        else:
            im, x, y = self.o.show(rotation=rot)

        im = copy(im)
        im.thumbnail((72, 72), Image.NEAREST)
        coords = (int(34-im.size[0]/2), int(36-im.size[1]/2))

        canvas = Image.new('RGBA', (72, 72))
        canvas.paste(im, coords)
        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)


class SpriteImportUi(QDialog):
    def __init__(self, layers_incoming, selected_index, layers_object):
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

        if selected_index >= 0:
            self.list_layers_incoming.setCurrentRow(selected_index)

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
