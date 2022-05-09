# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore

from rctobject import constants as cts

class settingsTabSS(QWidget):
    def __init__(self, editor, o):
        super().__init__()
        uic.loadUi('settingsSS.ui', self)
        
        self.editor = editor
        self.o = o
        
        self.tab_widget = self.findChild(QTabWidget, "tabWidget_settingsSS")
        self.tab_widget.currentChanged.connect(self.tabChanged)
        
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
        self.clearence_box = self.findChild(QDoubleSpinBox, "doubleSpinBox_clearence")
        
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

        self.object_name_field.textEdited.connect(self.nameChanged)
        self.object_name_lang_field.textEdited.connect(self.nameChangedLang)

        
        self.loadObjectSettings()
        
       
    def tabChanged(self, index):
        if index == 0:
            self.object_name_field.setText(self.o.data['strings']['name']['en-GB'])
        elif index == 2 and self.language_index == 0:
            self.object_name_lang_field.setText(self.o.data['strings']['name']['en-GB'])
        
        
    # bother with when other subtypes are introduced   
    def subtypeChanged(self, value):
        pass        
        
        
    def shapeChanged(self):
        value = self.shape_box.currentIndex()
        
        if value == 0:
            self.diagonal_box.setEnabled(True)
            if self.diagonal_box.isChecked():
                shape = self.o.Shape.QUARTERD
            else:
                shape = self.o.Shape.QUARTER

        elif value == 1:
            self.diagonal_box.setChecked(False)
            self.diagonal_box.setEnabled(False)
            shape = self.o.Shape.HALF

        elif value == 2:
            self.diagonal_box.setChecked(True)
            self.diagonal_box.setEnabled(False)
            shape = self.o.Shape.THREEQ
        
        elif value == 3:
             self.diagonal_box.setEnabled(True)
             if self.diagonal_box.isChecked():
                 shape = self.o.Shape.FULLD
             else:
                 shape = self.o.Shape.FULL

        self.o.changeShape(shape)
        
    def nameChanged(self, value):
        self.o.data['strings']['name']['en-GB'] = value
        
    def nameChangedLang(self, value):    
        if self.language_index == 0:
            self.o.data['strings']['name']['en-GB'] = value
            
    def languageChanged(self, value):
        lang = list(cts.languages)[self.language_index]
        self.o.data['strings']['name'][lang] = self.object_name_lang_field.text()

        self.language_index = value
        lang = list(cts.languages)[value]
        self.object_name_lang_field.setText(self.o.data['strings']['name'].get(lang,''))
        
        
        
    def loadObjectSettings(self):
         
        self.subtype_box.setCurrentIndex(self.o.subtype.value)
        self.shape_box.setCurrentIndex(self.o.shape.value)
        
        self.clearence_box.setValue(self.o.data['properties']['height'])
        
        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(self.o.data['properties'].get(flag, False))
                
        self.cursor_box.setCurrentIndex(cts.cursors.index(self.o.data['properties'].get('cursor','CURSOR_BLANK')))

        self.author_field.setText(self.o.data.get('authors',''))
        
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
        
        self.object_name_field.setText(self.o.data['strings']['name'].get('en-GB',''))
        self.object_name_lang_field.setText(self.o.data['strings']['name'].get('en-GB',''))
        
class spritesTabSS(QWidget):
    def __init__(self, editor, obj):
        super().__init__()
        uic.loadUi('spritesSS.ui', self)
        
        self.editor = editor
        self.obj = obj
        
        
        