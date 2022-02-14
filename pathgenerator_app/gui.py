# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 23:48:10 2022

@author: Daniel
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL.ImageQt import ImageQt
import sys
from os import getcwd

import generate_path as gen

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('pathgenerator.ui', self)
        
        self.generator = gen.pathGenerator()
        
        # Define Widgets
        self.buttonLoadBase = self.findChild(QPushButton, "pushButton_loadImageButton")
        self.buttonChangeOutputFolder = self.findChild(QPushButton, "pushButton_changeOutputFolder")
        self.buttonGenerate = self.findChild(QPushButton, "pushButton_generate")
        self.buttonSelectAll = self.findChild(QPushButton, "pushButton_selectAll")
        self.buttonClearAll = self.findChild(QPushButton, "pushButton_clearAll")
        self.buttonImportTemplate = self.findChild(QPushButton, "pushButton_importTemplate")
        self.checkboxAutoNaming = self.findChild(QCheckBox, "checkBox_autoNaming")
        self.checkboxAutoRotation= self.findChild(QCheckBox, "checkBox_autoRotation")
        self.checkboxPrimaryRemap= self.findChild(QCheckBox, "checkBox_primaryRemap")
        self.checkboxSecondaryRemap= self.findChild(QCheckBox, "checkBox_secondaryRemap")
        self.labelDisplayName = self.findChild(QLabel, "label_displayName")
        self.labelPrefix = self.findChild(QLabel, "label_prefix")
        self.labelSuffix = self.findChild(QLabel, "label_suffix")
        self.labelGenerateReturn = self.findChild(QLabel, "label_GenerateReturn")

        self.spinboxVersion = self.findChild(QDoubleSpinBox, "doubleSpinBox_version")
        
        self.lineeditAuthor = self.findChild(QLineEdit, "lineEdit_author")
        self.lineeditAuthorID = self.findChild(QLineEdit, "lineEdit_authorID")
        self.lineeditObjectID = self.findChild(QLineEdit, "lineEdit_objectID")
        self.lineeditPrefix = self.findChild(QLineEdit, "lineEdit_prefix")
        self.lineeditSuffix = self.findChild(QLineEdit, "lineEdit_suffix")
        self.lineeditOutputFolder = self.findChild(QLineEdit, "lineEdit_outputFolder")

        #self.scrollAreaTemplate = self.findChild(QScrollArea, "scrollArea")
        self.listwidgetTemplateList = self.findChild(QListWidget, "listWidget_templateList")
        
        self.spriteViewLabel = self.findChild(QLabel, "sprite_view")

        # Set defaults
        self.lineeditAuthor.setText(self.generator.settings['author'])
        self.lineeditAuthorID.setText(self.generator.settings['author_id'])
        self.lineeditSuffix.hide()        
        self.labelSuffix.hide()
        self.labelPrefix.setText('')
        
        self.lineeditOutputFolder.setText(getcwd())
        
        self.loadTemplates()
        
        
        # Add functions
        self.buttonLoadBase.clicked.connect(self.clickLoadBase)
        self.buttonSelectAll.clicked.connect(self.listwidgetTemplateList.selectAll)
        self.buttonClearAll.clicked.connect(self.listwidgetTemplateList.clearSelection)
        self.buttonImportTemplate.clicked.connect(self.clickImportTemplate)
        self.buttonChangeOutputFolder.clicked.connect(self.clickChangeOutputFolder)
        self.buttonGenerate.clicked.connect(self.clickGenerate)

        
        self.checkboxPrimaryRemap.stateChanged.connect(self.clickBoxPrimaryRemap)
        self.checkboxSecondaryRemap.stateChanged.connect(self.clickBoxSecondaryRemap)
        self.checkboxAutoNaming.stateChanged.connect(self.clickBoxAutoNaming)
        self.checkboxAutoRotation.stateChanged.connect(self.clickBoxAutoRotation)
        self.lineeditPrefix.textChanged.connect(self.updateDisplayName)
        self.lineeditSuffix.textChanged.connect(self.updateDisplayName)

        
        self.show()

    #Event functions
    def clickLoadBase(self):
        
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Base Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")
        
        if filepath:
            self.generator.loadBase(filepath)
        
        self.updatePreview()
        
        self.checkboxPrimaryRemap.setChecked(self.generator.settings['hasPrimaryColour'])
        self.checkboxSecondaryRemap.setChecked(self.generator.settings['hasSecondaryColour'])

    def clickChangeOutputFolder(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))
        self.lineeditOutputFolder.setText(folder)
        
    def clickBoxPrimaryRemap(self,state):
        self.generator.settings['hasPrimaryColour'] = (state == QtCore.Qt.Checked)
        
    def clickBoxSecondaryRemap(self,state):
        self.generator.settings['hasSecondaryColour'] = (state == QtCore.Qt.Checked)
     
    def clickBoxAutoNaming(self,state):
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

        self.generator.setName(self.lineeditPrefix.text(),self.lineeditSuffix.text())
        self.generator.settings['author'] = [auth.strip() for auth in self.lineeditAuthor.text().split(',')]
        self.generator.settings['author_id'] = self.lineeditAuthorID.text()
        self.generator.settings['object_id'] = self.lineeditObjectID.text()
        self.generator.selected_templates = [sel.text() for sel in self.listwidgetTemplateList.selectedItems()]
        
        return_text = self.generator.generate(self.lineeditOutputFolder.text())
        
        self.labelGenerateReturn.setText(return_text)
   
            
            
    def clickBoxAutoRotation(self,state):
        self.generator.settings['autoRotate'] = (state == QtCore.Qt.Checked)

    def clickImportTemplate(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Template File", "", "Template File (*.template)")
        
        if filepath:
            name = self.generator.loadTemplate(filepath)
            
            if name:
                self.listwidgetTemplateList.addItem(name)
            else:
                pass
           
        
        
        
    #Auxiliary functions
        
    def linkGenerator(self, pathgenerator):
        self.generator = pathgenerator        
        
    def updatePreview(self):
        image = ImageQt(self.generator.preview)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.spriteViewLabel.setPixmap(pixmap)
     
    def updateDisplayName(self):
        if self.generator.settings['autoNaming']:
            self.labelDisplayName.setText(self.lineeditPrefix.text() + ' Fulltile ' + self.lineeditSuffix.text())
        else:
            self.labelDisplayName.setText(self.lineeditPrefix.text())
        
    def loadTemplates(self):
        for name in self.generator.templates.keys():
            self.listwidgetTemplateList.addItem(name)
        
        
        
        
        
        
        
        
app = QApplication(sys.argv)
window = Ui()
app.exec_()
