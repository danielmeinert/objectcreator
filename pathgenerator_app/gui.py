# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 23:48:10 2022

@author: Daniel
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from os import getcwd

import generate_path as gen
import resources_rc


class Ui(QMainWindow):
    def __init__(self, generator):
        super(Ui, self).__init__()
        uic.loadUi('pathgenerator.ui', self)

        self.generator = generator

        # Define Widgets
        self.buttonLoadBase = self.findChild(
            QPushButton, "pushButton_loadImageButton")
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

        #self.scrollAreaTemplate = self.findChild(QScrollArea, "scrollArea")
        self.listwidgetTemplateList = self.findChild(
            QListWidget, "listWidget_templateList")

        self.spriteViewLabel = self.findChild(QLabel, "sprite_view")

        # Set defaults
        self.lineeditAuthor.setText(self.generator.settings['author'])
        self.lineeditAuthorID.setText(self.generator.settings['author_id'])
        self.lineeditSuffix.hide()
        self.labelSuffix.hide()
        self.labelPrefix.setText('')

        self.lineeditOutputFolder.setText(getcwd())

        self.comboboxRemapToColor.addItems(
            list(self.generator.current_palette.color_dict))
        self.comboboxRemapToColor.setCurrentIndex(
            self.generator.current_palette.color_dict['1st Remap'])

        self.loadTemplates()

        # Add functions
        self.buttonLoadBase.clicked.connect(self.clickLoadBase)
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

        self.checkboxAutoNaming.stateChanged.connect(self.clickBoxAutoNaming)
        self.checkboxAutoRotation.stateChanged.connect(
            self.clickBoxAutoRotation)
        self.lineeditPrefix.textChanged.connect(self.updateDisplayName)
        self.lineeditSuffix.textChanged.connect(self.updateDisplayName)

        self.show()

    # Event functions
    def clickLoadBase(self):

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Base Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            self.generator.loadBase(filepath)

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

    # Auxiliary functions

    def linkGenerator(self, pathgenerator):
        self.generator = pathgenerator

    def updatePreview(self):
        canvas = Image.new('RGBA', (172, 132))
        canvas.paste(
            self.generator.base.show(), (86+self.generator.base.x, 50+self.generator.base.y), self.generator.base.image)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.spriteViewLabel.setPixmap(pixmap)

    def updateDisplayName(self):
        if self.generator.settings['autoNaming']:
            self.labelDisplayName.setText(
                self.lineeditPrefix.text() + ' Fulltile ' + self.lineeditSuffix.text())
        else:
            self.labelDisplayName.setText(self.lineeditPrefix.text())

    def loadTemplates(self):
        for name in self.generator.templates.keys():
            self.listwidgetTemplateList.addItem(name)


app = QApplication(sys.argv)
generator = gen.pathGenerator()
window = Ui(generator)
app.exec_()
