# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
from copy import copy
import os.path


from rctobject import constants as cts

class objectTabSS(QWidget):
    def __init__(self, o, filepath = None, author_id = None):
        super().__init__()
        
        self.o = o
        self.lastpath = filepath
        self.saved = False

        layout = QHBoxLayout()
        
        self.spritesTab = spritesTabSS(o, self)
        self.settingsTab = settingsTabSS(o, self, author_id)
        
        layout.addWidget(self.spritesTab)
        layout.addWidget(self.settingsTab)
        
        self.setLayout(layout)
        
    def saveObject(self, get_path):
        if self.settingsTab.author_id_field.text():
            name = f"{self.settingsTab.author_id_field.text()}.{self.o.data.get('id','')}" 
        else:
            name = self.o.data.get('id','')
            
        if get_path or not self.saved:
            if self.lastpath:
                path = f"{self.lastpath}/{name}" 
            else:
                path = name
    
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Object", path,"Parkobj Files (*.parkobj)")
            if filepath.endswith('.parkobj.parkobj'):
                filepath = filepath[:-8]
        else:
            filepath = f"{self.lastpath}/{name}" 
            
        if self.settingsTab.checkBox_remapCheck.isChecked():
            for path, sprite in self.o.sprites.items():
                if sprite.checkPrimaryColor():
                    self.o.data['properties']['hasPrimaryColour'] = True
                    break
            for path, sprite in self.o.sprites.items():
                if sprite.checkSecondaryColor():
                    self.o.data['properties']['hasSecondaryColour'] = True
                    break
            for path, sprite in self.o.sprites.items():
                if sprite.checkTertiaryColor():
                    self.o.data['properties']['hasTertiaryColour'] = True
                    break
        
        if filepath:
            filepath, name = os.path.split(filepath)
            self.lastpath = filepath
            self.o.save(filepath, name = name, include_originalId = self.settingsTab.checkbox_keepOriginalId.isChecked())
            self.saved = True
            
            
        
            
            

class settingsTabSS(QWidget):
    def __init__(self, o, object_tab, author_id):
        super().__init__()
        uic.loadUi('settingsSS.ui', self)
        
        self.o = o
        self.object_tab = object_tab
        
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
        
        checkbox = self.findChild(QCheckBox, 'checkBox_remapCheck')
        checkbox.stateChanged.connect(self.flagRemapChanged)
        
        self.checkbox_keepOriginalId = self.findChild(QCheckBox, "checkBox_keepOrginalId")
        
        self.loadObjectSettings(author_id)
        
       
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
        
    def authorChanged(self, value):
        self.o.data['authors'] = value 
        
    def authorIdChanged(self, value):
        self.object_tab.saved = False
        
    def idChanged(self, value):
        self.o.data['id'] = value
        self.object_tab.saved = False
        
        
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
      
    def flagChanged(self, value, flag):
        self.o['properties'][flag] = bool(value)

    def flagRemapChanged(self, value):
        self.hasPrimaryColour.setEnabled(not value)    
        self.hasSecondaryColour.setEnabled(not value)    
        self.hasTertiaryColour.setEnabled(not value)    

        
    def loadObjectSettings(self, author_id = None):
         
        self.subtype_box.setCurrentIndex(self.o.subtype.value)
        self.shape_box.setCurrentIndex(self.o.shape.value)
        
        self.clearence_box.setValue(self.o.data['properties']['height'])
        
        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(self.o.data['properties'].get(flag, False))
                
        self.cursor_box.setCurrentIndex(cts.cursors.index(self.o.data['properties'].get('cursor','CURSOR_BLANK')))

        self.author_field.setText(self.o.data.get('authors',''))
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
        
        self.object_name_field.setText(self.o.data['strings']['name'].get('en-GB',''))
        self.object_name_lang_field.setText(self.o.data['strings']['name'].get('en-GB',''))
   
        
class spritesTabSS(QWidget):
    def __init__(self, o, object_tab):
        super().__init__()
        uic.loadUi('spritesSS.ui', self)
        
        self.o = o
        self.object_tab = object_tab
        
        
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
        
        
        
        self.offset = 16 if (self.o.shape == self.o.Shape.QUARTER or self.o.shape == self.o.Shape.QUARTERD) else 32
        self.sprite_preview = [self.sprite_view_preview0,self.sprite_view_preview1,self.sprite_view_preview2,self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent= (lambda e, rot=rot: self.previewClicked(rot))
            self.updatePreview(rot)
            
        self.previewClicked(0)
    
        
    def previewClicked(self, rot):
        old_rot = self.o.rotation
        self.sprite_preview[old_rot].setStyleSheet("background-color :  black; border:none;") 
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
     
    def updateMainView(self):
        im, x, y = self.o.show()
        coords = (76+x, 200+y)
        
        canvas = Image.new('RGBA', (152, 271))
        canvas.paste(im, coords, im)
        #canvas.paste(self.frame_image, self.frame_image)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main.setPixmap(pixmap)
        
        self.updatePreview(self.o.rotation)
        
    def updatePreview(self,rot):
        im, x, y = self.o.show(rotation = rot)
        im = copy(im)
        
        im.thumbnail((72, 72), Image.NEAREST)
        coords = (int(36-im.size[0]/2),int(36-im.size[1]/2))
        # if im.size[1] > 72:
        #     
        #     coords = (36+x,0)
        # else:
        #     coords = (36+x, 40+y)
        
        canvas = Image.new('RGBA', (72, 72))
        canvas.paste(im, coords, im)
        #canvas.paste(self.frame_image, self.frame_image)
        
        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)
        
        
        
        
        
        
  
        
        
        
        
        
        
        
        
        
        
        
        
        
        