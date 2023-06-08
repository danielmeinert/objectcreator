# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""


from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QTabWidget, QDial, QSlider, QScrollBar, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import traceback
import sys

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


import io
from os import getcwd
from os.path import splitext, split, abspath,join
from json import load as jload
from json import dump as jdump
from enum import Enum

from customwidgets import ColorSelectWidget, ToolBoxWidget
import customwidgets as cwdg
import widgets as wdg
import auxiliaries as aux

from rctobject import constants as cts
from rctobject import objects as obj
from rctobject import palette as pal

import ctypes

VERSION = 0.2


myappid = f'objectcreator.{VERSION}' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindowUi(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/main_window.ui'), self)
        self.setWindowIcon(QtGui.QIcon(aux.resource_path("gui/icon.png")))
        self.setWindowTitle(f'Object Creator - {VERSION}')

        self.loadSettings()
        self.bounding_boxes = aux.BoundingBoxes()
        
        
        self.setAcceptDrops(True)

        ##### Tabs
        self.new_object_count = 1
        self.new_sprite_count = 1


        self.object_tabs = self.findChild(
            QTabWidget, "tabWidget_objects")
        self.sprite_tabs = self.findChild(
            QTabWidget, "tabWidget_sprites")

        self.object_tabs.removeTab(0)
        self.sprite_tabs.removeTab(0)

        # Tab actions
        self.object_tabs.tabCloseRequested.connect(self.closeObject)
        self.object_tabs.currentChanged.connect(self.changeObjectTab)
        self.sprite_tabs.currentChanged.connect(self.changeSpriteTab)


        #### Tools
        widget_tool_box = self.findChild(QWidget, "widget_tool_box")
        self.toolbox = ToolBoxWidget()
        self.giveTool = self.toolbox.giveTool
        self.giveBrush = self.toolbox.giveBrush
        self.giveBrushsize = self.toolbox.giveBrushsize
        self.giveAirbrushStrength = self.toolbox.giveAirbrushStrength

        widget_tool_box.layout().addWidget(self.toolbox)


        # Color Panel
        self.widget_color_panel = self.findChild(QGroupBox, "groupBox_selectedColor")

        self.color_select_panel = ColorSelectWidget(pal.orct, True, True, True)
        self.giveActiveShade = self.color_select_panel.giveActiveShade #this is a function wrapper to get the current active shade

        self.widget_color_panel.layout().addWidget(self.color_select_panel)

        # Color Manipulations
        self.checkbox_all_views = self.findChild(
            QCheckBox, "checkBox_allViews")

        self.button_remap_to = self.findChild(
            QPushButton, "pushButton_remapTo")
        self.combobox_remap_to_color = self.findChild(
            QComboBox, "comboBox_remapToColor")

        self.combobox_remap_to_color.addItems(
            list(self.current_palette.color_dict))
        self.combobox_remap_to_color.setCurrentIndex(
            self.current_palette.color_dict['1st Remap'])

        self.button_incr_brightness = self.findChild(
            QPushButton, "pushButton_incrBrightness")
        self.button_decr_brightness = self.findChild(
            QPushButton, "pushButton_decrBrightness")
        self.button_remove_color = self.findChild(
            QPushButton, "pushButton_deleteColor")

        self.button_remap_to.clicked.connect(self.colorRemapTo)
        self.button_incr_brightness.clicked.connect(lambda x, step = 1: self.colorChangeBrightness(step))
        self.button_decr_brightness.clicked.connect(lambda x, step = -1: self.colorChangeBrightness(step))
        self.button_remove_color.clicked.connect(self.colorRemove)


        #### Menubar
        self.actionSmallScenery.triggered.connect(lambda x: self.newObject(cts.Type.SMALL))
        self.actionOpenFile.triggered.connect(self.openObjectFile)
        self.actionSave.triggered.connect(self.saveObject)
        self.actionSaveObjectAt.triggered.connect(self.saveObjectAt)

        self.actionNewSprite.triggered.connect(self.spriteNew)
        self.actionUndo.triggered.connect(self.spriteUndo)
        self.actionRedo.triggered.connect(self.spriteRedo)
        self.actionPasteSprite.triggered.connect(self.spritePaste)
        self.actionCopySprite.triggered.connect(self.spriteCopy)

        self.actionSettings.triggered.connect(self.changeSettings)
        self.actionBlack.triggered.connect(lambda x, mode=0: self.setCurrentImportColor(mode))
        self.actionWhite.triggered.connect(lambda x, mode=1: self.setCurrentImportColor(mode))
        self.actionUpper_Left_Pixel.triggered.connect(lambda x, mode=2: self.setCurrentImportColor(mode))
        self.actionCustom_Color.triggered.connect(lambda x, mode=3: self.setCurrentImportColor(mode))

        self.actionPaletteOpenRCT.triggered.connect(lambda x, palette=0: self.setCurrentPalette(palette))
        self.actionPaletteOld.triggered.connect(lambda x, palette=1: self.setCurrentPalette(palette))


        #Load empty object
        self.newObject(cts.Type.SMALL)

        self.show()

    def loadSettings(self):
        try:
            self.settings = jload(fp=open('config.json'))
        except FileNotFoundError:
            self.settings = {}
            self.changeSettings(update_widgets = False)

            #If user refused to enter settings, use hard coded settings
            if not self.settings:
                self.settings['openpath'] = "%USERPROFILE%/Documents/OpenRCT2"
                self.settings['savedefault'] = ''
                self.settings['opendefault'] =  "%USERPROFILE%/Documents/OpenRCT2/object"
                self.settings['author'] = ''
                self.settings['author_id'] = ''
                self.settings['no_zip'] = False
                self.settings['version'] = '1.0'
                self.settings['transparency_color'] = 0
                self.settings['import_color'] = [0,0,0]
                self.settings['palette'] = 0
                self.settings['history_maximum'] = 5

                self.settings['small_scenery_defaults'] = {}

        self.openpath = self.settings['openpath']
        self.last_open_folder = self.settings.get('opendefault', None)
        self.setCurrentImportColor(self.settings['transparency_color'])
        self.setCurrentPalette(self.settings['palette'], update_widgets = False)

    def saveSettings(self):
        path = getcwd()
        with open(f'{path}/config.json', mode='w') as file:
            jdump(obj=self.settings, fp=file, indent=2)

    def changeSettings(self, update_widgets = True):
        dialog = wdg.ChangeSettingsUi(self.settings)

        if dialog.exec():
            self.settings = dialog.ret

            self.openpath = self.settings['openpath']
            self.setCurrentImportColor(self.settings['transparency_color'])
            self.setCurrentPalette(self.settings['palette'], update_widgets = update_widgets)

            self.saveSettings()

    def setCurrentImportColor(self, mode):
        if mode == 0:
            self.current_import_color = (0,0,0)
            self.actionBlack.setChecked(True)
            self.actionWhite.setChecked(False)
            self.actionUpper_Left_Pixel.setChecked(False)
            self.actionCustom_Color.setChecked(False)
        elif mode == 1:
            self.current_import_color = (255,255,255)
            self.actionBlack.setChecked(False)
            self.actionWhite.setChecked(True)
            self.actionUpper_Left_Pixel.setChecked(False)
            self.actionCustom_Color.setChecked(False)
        elif mode == 2:
            self.current_import_color = None
            self.actionBlack.setChecked(False)
            self.actionWhite.setChecked(False)
            self.actionUpper_Left_Pixel.setChecked(True)
            self.actionCustom_Color.setChecked(False)
        elif mode == 3:
            self.current_import_color = self.settings.get('import_color', (0,0,0))
            self.actionBlack.setChecked(False)
            self.actionWhite.setChecked(False)
            self.actionUpper_Left_Pixel.setChecked(False)
            self.actionCustom_Color.setChecked(True)

    def setCurrentPalette(self, palette, update_widgets = True):
        if palette == 0:
            self.current_palette = pal.orct
            self.actionPaletteOpenRCT.setChecked(True)
            self.actionPaletteOld.setChecked(False)
        elif palette == 1:
            self.current_palette = pal.green_remap
            self.actionPaletteOpenRCT.setChecked(False)
            self.actionPaletteOld.setChecked(True)

        if update_widgets:
            self.color_select_panel.switchPalette(self.current_palette)
            for index in range(self.object_tabs.count()):
                tab = self.object_tabs.widget(index)
                tab.o.switchPalette(self.current_palette)
                tab.spritesTab.updateAllViews()

    def changeObjectTab(self, index):
        object_tab = self.object_tabs.widget(index)
        if object_tab and object_tab.locked:
            self.sprite_tabs.setCurrentIndex(self.sprite_tabs.indexOf(object_tab.locked_sprite_tab))

    def changeSpriteTab(self, index):
        sprite_tab = self.sprite_tabs.widget(index)
        if sprite_tab and sprite_tab.locked:
            self.object_tabs.setCurrentIndex(self.object_tabs.indexOf(sprite_tab.object_tab))

    def newObject(self, obj_type = cts.Type.SMALL):
        o = obj.newEmpty(obj_type)
        name = f'Object {self.new_object_count}'
        self.new_object_count += 1

        if not self.current_palette == pal.orct:
            o.switchPalette(self.current_palette)

        object_tab = wdg.ObjectTabSS(o, self, author = self.settings['author'], author_id = self.settings['author_id'])
        sprite_tab = wdg.SpriteTab(self, object_tab)

        object_tab.lockWithSpriteTab(sprite_tab)

        object_tab.settingsTab.setDefaults()

        self.object_tabs.addTab(object_tab, name)
        self.object_tabs.setCurrentWidget(object_tab)

        self.sprite_tabs.addTab(sprite_tab, f"{name} (locked)")
        self.sprite_tabs.setCurrentWidget(sprite_tab)

    def closeObject(self, index):
        object_tab = self.object_tabs.widget(index)
        if object_tab.locked:
            self.sprite_tabs.removeTab(self.sprite_tabs.indexOf(object_tab.locked_sprite_tab))

        self.object_tabs.removeTab(index)

    def openObjectFile(self):
        folder = self.last_open_folder
        if not folder:
            folder = getcwd()
        filepaths, _ = QFileDialog.getOpenFileNames(
            self, "Open Object", folder, "All Object Type Files (*.parkobj *.DAT *.json);; Parkobj Files (*.parkobj);; DAT files (*.DAT);; JSON Files (*.json);; All Files (*.*)")

        if filepaths:
            for filepath in filepaths:
                try:
                    o = obj.load(filepath, openpath = self.openpath)
                    name = o.data.get('id', '').split('.',2)[-1]
                    if not name:
                        if o.old_id:
                            name = o.old_id
                        else:
                            name = f'Object {self.new_object_count}'
                            self.new_object_count += 1
                except Exception as e:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("Failed to load object")
                    msg.setInformativeText(str(e))
                    msg.show()
                    return


                extension = splitext(filepath)[1].lower()
                author_id = None
                filepath, filename = split(filepath)
                if extension == '.parkobj':
                    # We assume that when the filename has more than 2 dots that the first part corresponds to the author id
                    if len(filename.split('.')) > 2:
                        author_id = filename.split('.')[0]


                if not self.current_palette == pal.orct:
                    o.switchPalette(self.current_palette)


                object_tab = wdg.ObjectTabSS(o, self, filepath, author_id = author_id)

                sprite_tab = wdg.SpriteTab(self, object_tab)

                self.object_tabs.addTab(object_tab, name)
                self.object_tabs.setCurrentWidget(object_tab)
                self.sprite_tabs.addTab(sprite_tab,  f"{name} (locked)")
                self.sprite_tabs.setCurrentWidget(sprite_tab)

            else:
                self.last_open_folder = filepath

    def saveObject(self):
        widget = self.object_tabs.currentWidget()

        widget.saveObject(get_path = False)

    def saveObjectAt(self):
        widget = self.object_tabs.currentWidget()

        widget.saveObject(get_path = True)

    def spriteNew(self):
        name = f'Sprite {self.new_sprite_count}'
        self.new_sprite_count += 1
        sprite_tab = wdg.SpriteTab(self)

        self.sprite_tabs.addTab(sprite_tab, f"{name}")
        self.sprite_tabs.setCurrentWidget(sprite_tab)

    def spriteUndo(self):
        widget = self.sprite_tabs.currentWidget()

        widget.undo()

    def spriteRedo(self):
        widget = self.sprite_tabs.currentWidget()

        widget.redo()

    def spritePaste(self):
        widget = self.sprite_tabs.currentWidget()

        widget.paste()

    def spriteCopy(self):
        widget = self.sprite_tabs.currentWidget()

        widget.copy()

    def colorRemapTo(self):
        color_remap = self.combobox_remap_to_color.currentText()
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.object_tabs.currentWidget()

            widget.colorRemapToAll(color_remap, selected_colors)

        else:
            widget = self.sprite_tabs.currentWidget()

            widget.colorRemap(color_remap, selected_colors)


    def colorChangeBrightness(self, step):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.object_tabs.currentWidget()

            widget.colorChangeBrightnessAll(step, selected_colors)

        else:
            widget = self.sprite_tabs.currentWidget()

            widget.colorChangeBrightness(step, selected_colors)

    def colorRemove(self):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.object_tabs.currentWidget()

            widget.colorRemoveAll(selected_colors)

        else:
            widget = self.sprite_tabs.currentWidget()

            widget.colorRemove(selected_colors)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Control:
            self.toolbox.selectTool(cwdg.Tools.EYEDROPPER)

    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_Control:
            self.toolbox.restoreTool()
        
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            for url in e.mimeData().urls():
                filepath = url.toLocalFile()
                extension = splitext(filepath)[1].lower()
                
                if extension in ['.parkobj', '.dat', '.json']:
                    e.accept()
        else:
            e.ingore()
            
    def dropEvent(self, e):
        for url in e.mimeData().urls():
            filepath = url.toLocalFile()
            extension = splitext(filepath)[1].lower()
            
            if extension in ['.parkobj', '.dat', '.json']:
                try:
                    o = obj.load(filepath, openpath = self.openpath)
                    name = o.data.get('id', '').split('.',2)[-1]
                    if not name:
                        if o.old_id:
                            name = o.old_id
                        else:
                            name = f'Object {self.new_object_count}'
                            self.new_object_count += 1
                except Exception as e:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("Failed to load object")
                    msg.setInformativeText(str(e))
                    msg.show()
                    return
    
                author_id = None
                filepath, filename = split(filepath)
                if extension == '.parkobj':
                    # We assume that when the filename has more than 2 dots that the first part corresponds to the author id
                    if len(filename.split('.')) > 2:
                        author_id = filename.split('.')[0]
    
    
                if not self.current_palette == pal.orct:
                    o.switchPalette(self.current_palette)
    
    
                object_tab = wdg.ObjectTabSS(o, self, filepath, author_id = author_id)
    
                sprite_tab = wdg.SpriteTab(self, object_tab)
    
                self.object_tabs.addTab(object_tab, name)
                self.object_tabs.setCurrentWidget(object_tab)
                self.sprite_tabs.addTab(sprite_tab,  f"{name} (locked)")
                self.sprite_tabs.setCurrentWidget(sprite_tab)
    
            else:
                self.last_open_folder = filepath
            


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)


    sys._excepthook(exc_type, exc_value, exc_tb)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Error Trapper")
    msg.setText("Runtime error:")
    msg.setInformativeText(tb)
    msg.exec_()
    #sys.exit()

sys._excepthook = sys.excepthook
sys.excepthook = excepthook


def main():
    # if not QApplication.instance():
    #     app = QApplication(sys.argv)
    # else:
    #     app = QApplication.instance()

    app = QApplication(sys.argv)



    main = MainWindowUi()
    main.show()
    app.exec_()


    return main

if __name__ == '__main__':
    m = main()