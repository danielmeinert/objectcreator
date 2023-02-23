# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image, ImageGrab
from PIL.ImageQt import ImageQt
from copy import copy
import io
import os.path
from os import getcwd

from customwidgets import remapColorSelectWidget

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
        self.sprite_tab = False
        

        layout = QHBoxLayout()

        self.spritesTab = spritesTabSS(o, self)
        self.settingsTab = settingsTabSS(o, self, self.spritesTab, author, author_id)

        layout.addWidget(self.spritesTab)
        layout.addWidget(self.settingsTab)

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
            self.o.save(filepath, name = name, no_zip = self.main_window.settings['no_zip'], include_originalId = self.settingsTab.checkbox_keepOriginalId.isChecked())
            self.saved = True

    def lockWithSpriteTab(self, sprite_tab):
        self.locked = True
        self.sprite_tab = sprite_tab

    def unlockSpriteTab(self):
        self.locked = False
        self.sprite_tab = None
        
    def colorRemapToAllViews(self, color_remap, selected_colors):
        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.remapColor(color, color_remap)
                
        self.spritesTab.updateAllViews()

    def colorRemapCurrentView(self, color_remap, selected_colors):
        sprite = self.o.giveSprite()
        for color in selected_colors:
            sprite.remapColor(color, color_remap)
                
        self.spritesTab.updateMainView()


class settingsTabSS(QWidget):
    def __init__(self, o, object_tab, sprites_tab, author, author_id):
        super().__init__()
        uic.loadUi('settingsSS.ui', self)

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

        self.doubleSpinBox_price.valueChanged.connect(lambda value, name = 'price': self.spinBoxChanged(value, name))
        self.doubleSpinBox_removalPrice.valueChanged.connect(lambda value, name = 'removalPrice': self.spinBoxChanged(value, name))
        self.doubleSpinBox_version.valueChanged.connect(lambda value, name = 'version': self.spinBoxChanged(value, name))

        checkbox = self.findChild(QCheckBox, 'checkBox_remapCheck')
        checkbox.stateChanged.connect(self.flagRemapChanged)

        self.checkbox_keepOriginalId = self.findChild(QCheckBox, "checkBox_keepOrginalId")

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

        self.cursor_box.setCurrentIndex(cts.cursors.index(self.o['properties'].get('cursor','CURSOR_BLANK')))

        if author:
            self.author_field.setText(author)
        else:
            authors = ', '.join(self.o.data.get('authors',''))
            self.author_field.setText(authors)

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

        self.doubleSpinBox_price.setValue(self.o['properties'].get('price', 1))
        self.doubleSpinBox_removalPrice.setValue(self.o['properties'].get('removalPrice', 1))
        self.doubleSpinBox_version.setValue(float(self.o.data.get('version',1.0)))

    def setDefaults(self):

        settingsSS = self.main_window.settings['small_scenery_defaults']

        for flag in settingsSS:
            checkbox = self.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(settingsSS.get(flag, False))

        self.doubleSpinBox_price.setValue(settingsSS.get('price', 1))
        self.doubleSpinBox_removalPrice.setValue(settingsSS.get('removalPrice', 1))
        self.doubleSpinBox_version.setValue(settingsSS.get('version',1.0))

        self.cursor_box.setCurrentIndex(cts.cursors.index(settingsSS.get('cursor','CURSOR_BLANK')))


class spritesTabSS(QWidget):
    def __init__(self, o, object_tab):
        super().__init__()
        uic.loadUi('spritesSS.ui', self)

        self.o = o
        self.object_tab = object_tab
        self.main_window = object_tab.main_window

        main_widget = self.findChild(QGroupBox, "groupBox_spriteSS")

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

        # Buttons auxiliary
        self.buttonBoundingBox =  self.findChild(
            QToolButton, "toolButton_boundingBox")

        self.buttonBoundingBox.clicked.connect(self.updateMainView)

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


        self.offset = 16 if (self.o.shape == obj.SmallScenery.Shape.QUARTER or self.o.shape == obj.SmallScenery.Shape.QUARTERD) else 32
        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1, self.sprite_view_preview2, self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent = (lambda e, rot=rot: self.previewClicked(rot))
            self.updatePreview(rot)


        # Remap Color Panel
        groupRemap = self.findChild(QGroupBox, 'groupBox_remap')
        coords_group = (groupRemap.x(),groupRemap.y())

        self.buttonFirstRemap = self.findChild(QPushButton, 'pushButton_firstRemap')
        self.firstRemapSelectPanel = remapColorSelectWidget(pal.orct, main_widget, self.clickChangeRemap, "1st Remap", self.buttonFirstRemap)
        self.firstRemapSelectPanel.setGeometry(coords_group[0] + self.buttonFirstRemap.x(), coords_group[1] +  self.buttonFirstRemap.y()-50, 104, 52)
        self.firstRemapSelectPanel.hide()
        self.buttonFirstRemap.clicked.connect(lambda x, panel = self.firstRemapSelectPanel: self.clickRemapButton(panel = panel))

        self.buttonSecondRemap = self.findChild(QPushButton, 'pushButton_secondRemap')
        self.secondRemapSelectPanel = remapColorSelectWidget(pal.orct, main_widget, self.clickChangeRemap, "2nd Remap", self.buttonSecondRemap)
        self.secondRemapSelectPanel.setGeometry(coords_group[0] + self.buttonSecondRemap.x(), coords_group[1] +  self.buttonSecondRemap.y()-50, 104, 52)
        self.secondRemapSelectPanel.hide()
        self.buttonSecondRemap.clicked.connect(lambda x, panel = self.secondRemapSelectPanel: self.clickRemapButton(panel = panel))

        self.buttonThirdRemap = self.findChild(QPushButton, 'pushButton_thirdRemap')
        self.thirdRemapSelectPanel = remapColorSelectWidget(pal.orct, main_widget, self.clickChangeRemap, "3rd Remap", self.buttonThirdRemap)
        self.thirdRemapSelectPanel.setGeometry(coords_group[0] + self.buttonThirdRemap.x(), coords_group[1] +  self.buttonThirdRemap.y()-50, 104, 52)
        self.thirdRemapSelectPanel.hide()
        self.buttonThirdRemap.clicked.connect(lambda x, panel = self.thirdRemapSelectPanel: self.clickRemapButton(panel = panel))

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

    def copySpriteToView(self, view):
        rot = self.o.rotation

        self.o.setSprite(self.o.giveSprite(), rotation = view)

        self.updatePreview(view)

    def copySpriteToAllViews(self):
        rot = self.o.rotation

        for view in range(4):
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

    def clickRemapButton(self, panel):
        if panel.isVisible():
            panel.hide()
        else:
            panel.show()

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

        if self.buttonBoundingBox.isChecked():
            backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(self.o)
            canvas.paste(backbox, (76+coords_backbox[0], 200+coords_backbox[1]), backbox)


        #canvas.paste(self.frame_image, self.frame_image)
        canvas.paste(im, coords, im)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_view_main.setPixmap(pixmap)

        if self.object_tab.locked:
            self.object_tab.sprite_tab.updateView()

        self.updatePreview(self.o.rotation)

    def giveMainView(self):
        im, x, y = self.o.show()

        coords = (100+x, 100+y)

        canvas = Image.new('RGBA', (200, 200))

        if self.buttonBoundingBox.isChecked():
            backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(self.o)
            canvas.paste(backbox, (100+coords_backbox[0], 100+coords_backbox[1]), backbox)


        #canvas.paste(self.frame_image, self.frame_image)
        canvas.paste(im, coords, im)

        return canvas


    def updatePreview(self,rot):
        im, x, y = self.o.show(rotation = rot)
        im = copy(im)

        im.thumbnail((72, 72), Image.NEAREST)
        coords = (int(34-im.size[0]/2),int(36-im.size[1]/2))
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

    def updateAllViews(self):
        self.updateMainView()
        for rot in range(4):
            self.updatePreview(rot)

#### Sprites Tab

class SpriteTab(QWidget):
    def __init__(self, main_window, object_tab = None, filepath = None):
        super().__init__()
        uic.loadUi('sprite.ui', self)


        if object_tab:
            self.locked = True
            self.object_tab = object_tab
            self.sprite = object_tab.o.giveSprite()
        else:
            self.locked = False
            self.object_tab = None
            self.sprite = spr.Sprite()

        self.lastpath = filepath
        self.saved = False
        self.main_window = main_window


        self.updateView()

 
    def colorRemap(self, color_remap, selected_colors):
        if self.locked:
            self.object_tab.colorRemapCurrentView(color_remap, selected_colors)

    def updateView(self):

        if self.locked:
            canvas = self.object_tab.spritesTab.giveMainView()

            image = ImageQt(canvas)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.view.setPixmap(pixmap)



##### Settings window

class ChangeSettingsUi(QDialog):
    def __init__(self, settings):
        super().__init__()
        uic.loadUi('settings_window.ui', self)

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















