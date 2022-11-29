# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image, ImageGrab
from PIL.ImageQt import ImageQt
from copy import copy
import os.path

from os import getcwd

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal


class objectTabSS(QWidget):
    def __init__(self, o, filepath = None, author_id = None, settings = {}):
        super().__init__()
        
        self.o = o
        self.lastpath = filepath
        self.saved = False
        self.settings = settings

        layout = QHBoxLayout()
        
        self.spritesTab = spritesTabSS(o, self)
        self.settingsTab = settingsTabSS(o, self, self.spritesTab, author_id)
        
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
            while filepath.endswith('.parkobj'):
                filepath = filepath[:-8]
            filepath, name = os.path.split(filepath)
        else:
            filepath = self.lastpath
            
        if self.settingsTab.checkBox_remapCheck.isChecked():
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
            self.o.save(filepath, name = name, no_zip = self.settings['no_zip'], include_originalId = self.settingsTab.checkbox_keepOriginalId.isChecked())
            self.saved = True
            
 

class settingsTabSS(QWidget):
    def __init__(self, o, object_tab, sprites_tab, author_id):
        super().__init__()
        uic.loadUi('settingsSS.ui', self)
        
        self.o = o
        self.object_tab = object_tab
        self.sprites_tab = sprites_tab        
        
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
        self.o['authors'] = value 
        
    def authorIdChanged(self, value):
        self.object_tab.saved = False
        
    def idChanged(self, value):
        self.o['id'] = value
        self.object_tab.saved = False
        
        
    def nameChanged(self, value):
        self.o['strings']['name']['en-GB'] = value
        
    def nameChangedLang(self, value):    
        if self.language_index == 0:
            self.o['strings']['name']['en-GB'] = value
            
    def languageChanged(self, value):
        lang = list(cts.languages)[self.language_index]
        self.o['strings']['name'][lang] = self.object_name_lang_field.text()

        self.language_index = value
        lang = list(cts.languages)[value]
        self.object_name_lang_field.setText(self.o['strings']['name'].get(lang,''))
      
    def flagChanged(self, value, flag):
        self.o.flagChanged(flag, bool(value))
        
        self.sprites_tab.updateMainView()

    def flagRemapChanged(self, value):
        self.hasPrimaryColour.setEnabled(not bool(value))    
        self.hasSecondaryColour.setEnabled(not bool(value))    
        self.hasTertiaryColour.setEnabled(not bool(value))    

        
    def loadObjectSettings(self, author_id = None):
         
        self.subtype_box.setCurrentIndex(self.o.subtype.value)
        self.shape_box.setCurrentIndex(self.o.shape.value)
        
        self.clearence_box.setValue(self.o['properties']['height'])
        
        for flag in cts.Jsmall_flags:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(self.o['properties'].get(flag, False))
        
        checkbox = self.findChild(QCheckBox, 'isTree')
        checkbox.setChecked(self.o['properties'].get('isTree', False))
        
        self.cursor_box.setCurrentIndex(cts.cursors.index(self.o['properties'].get('cursor','CURSOR_BLANK')))

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
        
        self.object_name_field.setText(self.o['strings']['name'].get('en-GB',''))
        self.object_name_lang_field.setText(self.o['strings']['name'].get('en-GB',''))
   
        
class spritesTabSS(QWidget):
    def __init__(self, o, object_tab):
        super().__init__()
        uic.loadUi('spritesSS.ui', self)
        
        self.o = o
        self.object_tab = object_tab
        
        
        # Buttons load/reset
        self.buttonLoadImage = self.findChild(
            QPushButton, "pushButton_loadImage")
        self.buttonResetImage = self.findChild(
            QPushButton, "pushButton_resetImage")
        self.buttonResetOffsets = self.findChild(
            QPushButton, "pushButton_resetOffsets")
        
        self.buttonLoadImage.clicked.connect(self.loadImage)
        self.buttonResetImage.clicked.connect(self.resetImage)
        self.buttonResetOffsets.clicked.connect(self.resetOffsets)

        
        
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
        
        
        self.buttonCycleRotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")
        
        self.buttonCycleRotation.clicked.connect(self.cycleRotation)
        
        self.sprite_view_main.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sprite_view_main.customContextMenuRequested.connect(self.showSpriteMenu)

        
        self.offset = 16 if (self.o.shape == self.o.Shape.QUARTER or self.o.shape == self.o.Shape.QUARTERD) else 32
        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1, self.sprite_view_preview2, self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent = (lambda e, rot=rot: self.previewClicked(rot))
            self.updatePreview(rot)
            
        self.previewClicked(0)
    
    def loadImage(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            sprite = spr.Sprite.fromFile(filepath)
            sprite.x = -int(sprite.image.size[0]/2)
            sprite.y = -int(sprite.image.size[1]/2)
            sprite.x_base = int(sprite.x)
            sprite.y_base = int(sprite.y)
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
        paste_action = menu.addAction("Paste Sprite", self.pasteSpriteFromClipboard)
        action = menu.exec_(self.sprite_view_main.mapToGlobal(pos))
        
    def pasteSpriteFromClipboard(self):
        image = ImageGrab.grabclipboard()

        if image:
            image = pal.removeColorWhenImport(image.convert('RGBA'))
            
            sprite = spr.Sprite(image,(-int(image.size[0]/2),-int(image.size[1]/2)))
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
     
    def updateMainView(self):
        im, x, y = self.o.show()
        
        # if self.o['properties'].get('SMALL_SCENERY_FLAG_VOFFSET_CENTRE'):
        #     y -= 12
        #     y -= 2 if self.o['properties'].get('prohibitWalls') else 0
        
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
        
        
        
class ChangeSettingsUi(QDialog):
    def __init__(self, settings):
        super().__init__()
        uic.loadUi('settings_window.ui', self)
        
        self.setFixedSize(self.size())
         
        self.lineEdit_openpath.setText(settings.get('openpath'))
        self.lineEdit_savedefault.setText(settings.get('savedefault'))
        self.lineEdit_authorID.setText(settings.get('author_id'))
        self.lineEdit_author.setText(settings.get('author'))
        
        self.checkBox_nozip.setChecked(settings.get('no_zip', False))
        self.comboBox_transparencycolor.setCurrentIndex(settings.get('transparency_color', 0))
        self.spinBox_R.setValue(settings.get('import_color', (0,0,0))[0])
        self.spinBox_G.setValue(settings.get('import_color', (0,0,0))[1])
        self.spinBox_B.setValue(settings.get('import_color', (0,0,0))[2])
        self.doubleSpinBox_version.setValue(float(settings.get('version', 1)))
     
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
        
        self.pushButton_changeOpenpath.clicked.connect(lambda x, sender = self.lineEdit_openpath:
            self.clickChangeFolder(sender))
        self.pushButton_changeSaveDefault.clicked.connect(lambda x, sender = self.lineEdit_savedefault:
            self.clickChangeFolder(sender))

    
    def clickChangeFolder(self, sender):
        
        directory = sender.text() if sender.text() else getcwd()
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", directory = directory)
        if folder:
            sender.setText(folder)    
         
            
    def retrieveInputs(self):
        settings = {}
        
        settings['openpath'] = self.lineEdit_openpath.text()
        settings['author'] = self.lineEdit_author.text()
        settings['author_id'] = self.lineEdit_authorID.text()
        settings['no_zip'] = self.checkBox_nozip.isChecked()
        settings['version'] = self.doubleSpinBox_version.value()
        settings['transparency_color'] = self.comboBox_transparencycolor.currentIndex()
        settings['import_color'] = [self.spinBox_R.value(),self.spinBox_G.value(),self.spinBox_B.value()]
        
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
         
        ss_defaults['cursor'] = self.tab_SS_default.findChild(QComboBox, "comboBox_cursor").currentText()
        
        settings['small_scenery_defaults'] = ss_defaults
        
        return settings
        
    def accept(self):

         self.ret = self.retrieveInputs()         
         super().accept()       
        
  
        
        
        
        
        
        
        
        
        
        
        
        
        
        