# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 23:48:10 2022

@author: Daniel
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
import io
from os import getcwd

import generate_path as gen
import resources_rc


class Ui(QMainWindow):
    def __init__(self, generator):
        super(Ui, self).__init__()
        uic.loadUi('pathgenerator.ui', self)

        self.generator = generator
        self.loadFrame()

        # Define Widgets
        self.buttonLoadBase = self.findChild(
            QPushButton, "pushButton_loadImageButton")
        self.buttonFixToMask = self.findChild(
            QPushButton, "pushButton_fixToMask")
        self.buttonResetBase = self.findChild(
            QPushButton, "pushButton_resetBase")
        self.buttonChangeOutputFolder = self.findChild(
            QPushButton, "pushButton_changeOutputFolder")
        self.buttonGenerate = self.findChild(
            QPushButton, "pushButton_generate")
        self.buttonSelectAllTemplates = self.findChild(
            QPushButton, "pushButton_selectAllTemplates")
        self.buttonClearAllTemplates = self.findChild(
            QPushButton, "pushButton_clearAllTemplates")
        self.buttonColorsAll = self.findChild(
            QPushButton, "pushButton_colorsAll")
        self.buttonColorsInvert = self.findChild(
            QPushButton, "pushButton_colorsInvert")
        self.buttonRemapTo = self.findChild(
            QPushButton, "pushButton_remapTo")
        self.buttonIncrBrightness = self.findChild(
            QPushButton, "pushButton_incrBrightness")
        self.buttonDecrBrightness = self.findChild(
            QPushButton, "pushButton_decrBrightness")
        self.buttonImportTemplate = self.findChild(
            QPushButton, "pushButton_importTemplate")

        self.checkboxAutoNaming = self.findChild(
            QCheckBox, "checkBox_autoNaming")
        self.checkboxAutoRotation = self.findChild(
            QCheckBox, "checkBox_autoRotation")

        self.labelDisplayName = self.findChild(QLabel, "label_displayName")
        self.labelPrefix = self.findChild(QLabel, "label_prefix")
        self.labelSuffix = self.findChild(QLabel, "label_suffix")
        self.labelGenerateReturn = self.findChild(
            QLabel, "label_GenerateReturn")

        self.spinboxVersion = self.findChild(
            QDoubleSpinBox, "doubleSpinBox_version")

        self.comboboxRemapToColor = self.findChild(
            QComboBox, "comboBox_remapToColor")

        self.lineeditAuthor = self.findChild(QLineEdit, "lineEdit_author")
        self.lineeditAuthorID = self.findChild(QLineEdit, "lineEdit_authorID")
        self.lineeditObjectID = self.findChild(QLineEdit, "lineEdit_objectID")
        self.lineeditPrefix = self.findChild(QLineEdit, "lineEdit_prefix")
        self.lineeditSuffix = self.findChild(QLineEdit, "lineEdit_suffix")
        self.lineeditOutputFolder = self.findChild(
            QLineEdit, "lineEdit_outputFolder")

        # Checkboxes for Colors
        self.widgetColorPanel = self.findChild(QWidget, "widget_colorPanel")
        self.checkboxesColorPanel = {}
        for i, color in enumerate(self.generator.current_palette.color_dict):
            if i < 18:
                self.checkboxesColorPanel[color] = QCheckBox(
                    parent=self.widgetColorPanel)
                self.widgetColorPanel.layout().addWidget(
                    self.checkboxesColorPanel[color])
            else:
                self.checkboxesColorPanel[color] = self.findChild(
                    QCheckBox, "checkBox_primaryRemap")

            self.checkboxesColorPanel[color].stateChanged.connect(
                lambda state, color=color: self.clickBoxColorPanel(state, color))
            self.checkboxesColorPanel[color].setToolTip(color)

        # Sprite control buttons
        self.buttonSpriteLeft = self.findChild(
            QToolButton, "toolButton_left")
        self.buttonSpriteDown = self.findChild(
            QToolButton, "toolButton_down")
        self.buttonSpriteRight = self.findChild(
            QToolButton, "toolButton_right")
        self.buttonSpriteUp = self.findChild(
            QToolButton, "toolButton_up")
        self.buttonSpriteLeftRight = self.findChild(
            QToolButton, "toolButton_leftright")
        self.buttonSpriteUpDown = self.findChild(
            QToolButton, "toolButton_updown")

        self.listwidgetTemplateList = self.findChild(
            QListWidget, "listWidget_templateList")

        self.spriteViewLabel = self.findChild(QLabel, "sprite_view")

        # Set defaults
        self.lineeditAuthor.setText(self.generator.settings['author'])
        self.lineeditAuthorID.setText(self.generator.settings['author_id'])
        self.lineeditSuffix.hide()
        self.labelSuffix.hide()
        self.labelPrefix.setText('')

        self.lineeditOutputFolder.setText(f'{getcwd()}\\output')

        self.comboboxRemapToColor.addItems(
            list(self.generator.current_palette.color_dict))
        self.comboboxRemapToColor.setCurrentIndex(
            self.generator.current_palette.color_dict['1st Remap'])

        self.loadTemplates()

        # Add functions
        self.buttonLoadBase.clicked.connect(self.clickLoadBase)
        self.buttonFixToMask.clicked.connect(self.clickFixToMask)
        self.buttonResetBase.clicked.connect(self.clickResetBase)
        self.buttonSelectAllTemplates.clicked.connect(
            self.listwidgetTemplateList.selectAll)
        self.buttonClearAllTemplates.clicked.connect(
            self.listwidgetTemplateList.clearSelection)
        self.buttonImportTemplate.clicked.connect(self.clickImportTemplate)
        self.buttonChangeOutputFolder.clicked.connect(
            self.clickChangeOutputFolder)
        self.buttonGenerate.clicked.connect(self.clickGenerate)

        self.buttonColorsInvert.clicked.connect(self.clickColorsInvert)
        self.buttonColorsAll.clicked.connect(self.clickColorsAll)
        self.buttonRemapTo.clicked.connect(self.clickRemapTo)
        self.buttonIncrBrightness.clicked.connect(self.clickIncrBrightness)
        self.buttonDecrBrightness.clicked.connect(self.clickDecrBrightness)

        self.checkboxAutoNaming.stateChanged.connect(self.clickBoxAutoNaming)
        self.checkboxAutoRotation.stateChanged.connect(
            self.clickBoxAutoRotation)
        self.lineeditPrefix.textChanged.connect(self.updateDisplayName)
        self.lineeditSuffix.textChanged.connect(self.updateDisplayName)

        self.buttonSpriteLeft.clicked.connect(
            lambda x: self.clickSpriteControl('left'))
        self.buttonSpriteDown.clicked.connect(
            lambda x: self.clickSpriteControl('down'))
        self.buttonSpriteRight.clicked.connect(
            lambda x: self.clickSpriteControl('right'))
        self.buttonSpriteUp.clicked.connect(
            lambda x: self.clickSpriteControl('up'))
        self.buttonSpriteLeftRight.clicked.connect(
            lambda x: self.clickSpriteControl('leftright'))
        self.buttonSpriteUpDown.clicked.connect(
            lambda x: self.clickSpriteControl('updown'))

        self.buttonSpriteLeft.setAutoRepeat(True)
        self.buttonSpriteDown.setAutoRepeat(True)
        self.buttonSpriteRight.setAutoRepeat(True)
        self.buttonSpriteUp.setAutoRepeat(True)

        self.show()

    # Event functions
    def clickLoadBase(self):

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Base Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            self.generator.loadBase(filepath)

        self.updatePreview()

    def clickFixToMask(self):

        self.generator.fixBaseToMask()
        self.updatePreview()

    def clickResetBase(self):

        self.generator.base.resetSprite()
        self.updatePreview()

    def clickChangeOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory")
        if folder:
            self.lineeditOutputFolder.setText(folder)

    def clickBoxColorPanel(self, state, color):
        self.generator.selected_colors[color] = (
            state == QtCore.Qt.Checked)

    def clickBoxAutoNaming(self, state):
        self.generator.settings['autoNaming'] = (state == QtCore.Qt.Checked)
        if state == QtCore.Qt.Checked:
            self.lineeditSuffix.show()
            self.labelSuffix.show()
            self.labelPrefix.setText('Prefix')
        else:
            self.lineeditSuffix.hide()
            self.lineeditSuffix.setText('')
            self.labelSuffix.hide()
            self.labelPrefix.setText('')
        self.updateDisplayName()

    def clickGenerate(self):
        self.labelGenerateReturn.setText('')

        self.generator.setName(self.lineeditPrefix.text(),
                               self.lineeditSuffix.text())
        self.generator.settings['author'] = [
            auth.strip() for auth in self.lineeditAuthor.text().split(',')]
        self.generator.settings['author_id'] = self.lineeditAuthorID.text()
        self.generator.settings['object_id'] = self.lineeditObjectID.text()
        self.generator.selected_templates = [
            sel.text() for sel in self.listwidgetTemplateList.selectedItems()]

        return_text = self.generator.generate(self.lineeditOutputFolder.text())

        self.labelGenerateReturn.setText(return_text)

    def clickBoxAutoRotation(self, state):
        self.generator.settings['autoRotate'] = (state == QtCore.Qt.Checked)

    def clickImportTemplate(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Template File", "", "Template File (*.template)")

        if filepath:
            name = self.generator.loadTemplate(filepath)

            if name:
                self.listwidgetTemplateList.addItem(name)
            else:
                pass

    def clickColorsAll(self):
        for color, checkbox in self.checkboxesColorPanel.items():
            checkbox.setChecked(True)

    def clickColorsInvert(self):
        for color, checkbox in self.checkboxesColorPanel.items():
            checkbox.setChecked(not checkbox.checkState())

    def clickRemapTo(self):
        color_remap = self.comboboxRemapToColor.currentText()
        for color, selected in self.generator.selected_colors.items():
            if selected and color != color_remap:
                self.generator.base.remapColor(color, color_remap)

        self.updatePreview()

    def clickIncrBrightness(self):
        for color, selected in self.generator.selected_colors.items():
            if selected:
                self.generator.base.changeBrightnessColor(1, color)

        self.updatePreview()

    def clickDecrBrightness(self):
        for color, selected in self.generator.selected_colors.items():
            if selected:
                self.generator.base.changeBrightnessColor(-1, color)

        self.updatePreview()

    def clickSpriteControl(self, direction: str):
        if direction == 'left':
            self.generator.base.x -= 1
        elif direction == 'right':
            self.generator.base.x += 1
        elif direction == 'up':
            self.generator.base.y -= 1
        elif direction == 'down':
            self.generator.base.y += 1
        elif direction == 'leftright':
            self.generator.base.image = self.generator.base.image.transpose(
                Image.FLIP_LEFT_RIGHT)
        elif direction == 'updown':
            self.generator.base.image = self.generator.base.image.transpose(
                Image.FLIP_TOP_BOTTOM)

        self.updatePreview()

    # Auxiliary functions

    def linkGenerator(self, pathgenerator):
        self.generator = pathgenerator

    def updatePreview(self):
        canvas = Image.new('RGBA', (172, 132))
        canvas.paste(
            self.generator.base.show(), (86+self.generator.base.x, 50+self.generator.base.y), self.generator.base.image)
        canvas.paste(self.frame_image, self.frame_image)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.spriteViewLabel.setPixmap(pixmap)

    def updateDisplayName(self):
        if self.generator.settings['autoNaming']:
            self.labelDisplayName.setText(
                self.lineeditPrefix.text() + ' Fulltile ' + self.lineeditSuffix.text())
        else:
            self.labelDisplayName.setText(self.lineeditPrefix.text())

    def loadFrame(self):
        img = QtGui.QImage(":/images/res/frame.png")
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        self.frame_image = Image.open(io.BytesIO(buffer.data()))
        buffer.close()

    def loadTemplates(self):
        for name in self.generator.templates.keys():
            self.listwidgetTemplateList.addItem(name)
