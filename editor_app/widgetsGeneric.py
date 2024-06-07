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

from customwidgets import RemapColorSelectButton, ColorSelectWidget, ToolBoxWidget

import customwidgets as cwdg

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal
from rctobject import objects as obj


class SettingsTabAll(QWidget):
    """Proxy Class for all object types. initializeWidgets should be called after all members have been set."""

    def __init__(self):
        super().__init__()

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


class TabNamingMisc(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/tab_naming_misc.ui'), self)
