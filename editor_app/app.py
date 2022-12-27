# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox, QWidget,QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import traceback
import sys
import io
from os import getcwd
from os.path import splitext, split
from json import load as jload
from json import dump as jdump

from customwidgets import colorSelectWidget
import widgets as wdg
import auxiliaries as aux

from rctobject import constants as cts
from rctobject import objects as obj
from rctobject import palette as pal



class MainWindowUi(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)

        self.new_object_count = 1

        self.loadSettings()
        self.bounding_boxes = aux.BoundingBoxes()

        ##### Object Tabs ###
        self.objectTabs = self.findChild(
            QTabWidget, "tabWidget_objects")


        # Close tab action
        self.objectTabs.tabCloseRequested.connect(self.closeObject)

        #Load empty object
        self.objectTabs.removeTab(0)
        self.newObject(cts.Type.SMALL)

        #### Menubar
        self.actionSmallScenery.triggered.connect(lambda x: self.newObject(cts.Type.SMALL))
        self.actionOpenFile.triggered.connect(self.openObjectFile)
        self.actionSave.triggered.connect(self.saveObject)
        self.actionSaveObjectAt.triggered.connect(self.saveObjectAt)
        self.actionSettings.triggered.connect(self.changeSettings)

        self.actionBlack.triggered.connect(lambda x, mode=0: self.setCurrentImportColor(mode))
        self.actionWhite.triggered.connect(lambda x, mode=1: self.setCurrentImportColor(mode))
        self.actionUpper_Left_Pixel.triggered.connect(lambda x, mode=2: self.setCurrentImportColor(mode))
        self.actionCustom_Color.triggered.connect(lambda x, mode=3: self.setCurrentImportColor(mode))

        self.actionPaletteOpenRCT.triggered.connect(lambda x, palette=0: self.setCurrentPalette(palette))
        self.actionPaletteOld.triggered.connect(lambda x, palette=1: self.setCurrentPalette(palette))

        self.show()

    def loadSettings(self):
        try:
            self.settings = jload(fp=open('config.json'))
        except FileNotFoundError:
            self.settings = {}
            self.changeSettings(update_tabs = False)

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

        self.openpath = self.settings['openpath']
        self.setCurrentImportColor(self.settings['transparency_color'])
        self.setCurrentPalette(self.settings['palette'], update_tabs = False)



    def saveSettings(self):
        path = getcwd()
        with open(f'{path}/config.json', mode='w') as file:
            jdump(obj=self.settings, fp=file, indent=2)

    def changeSettings(self, update_tabs = True):
        dialog = wdg.ChangeSettingsUi(self.settings)

        if dialog.exec():
            self.settings = dialog.ret

            self.openpath = self.settings['openpath']
            self.setCurrentImportColor(self.settings['transparency_color'])
            self.setCurrentPalette(self.settings['palette'], update_tabs = update_tabs)

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

    def setCurrentPalette(self, palette, update_tabs = True):
        if palette == 0:
            self.current_palette = pal.orct
            self.actionPaletteOpenRCT.setChecked(True)
            self.actionPaletteOld.setChecked(False)
        elif palette == 1:
            self.current_palette = pal.green_remap
            self.actionPaletteOpenRCT.setChecked(False)
            self.actionPaletteOld.setChecked(True)

        if update_tabs:
            for index in range(self.objectTabs.count()):
                tab = self.objectTabs.widget(index)
                tab.o.switchPalette(self.current_palette)
                tab.spritesTab.updateAllViews()


    def newObject(self, obj_type = cts.Type.SMALL):
        o = obj.newEmpty(obj_type)
        name = f'Object {self.new_object_count}'
        self.new_object_count += 1

        if not self.current_palette == pal.orct:
            o.switchPalette(self.current_palette)

        tab = wdg.objectTabSS(o, self, author_id = self.settings['author_id'])

        self.objectTabs.addTab(tab, name)
        self.objectTabs.setCurrentWidget(tab)

    def closeObject(self, index):
        self.objectTabs.removeTab(index)

    def openObjectFile(self):


        filepaths, _ = QFileDialog.getOpenFileNames(
            self, "Open Object", self.settings.get('opendefault',''), "All Object Type Files (*.parkobj *.DAT *.json);; Parkobj Files (*.parkobj);; DAT files (*.DAT);; JSON Files (*.json);; All Files (*.*)")

        if filepaths:
            for filepath in filepaths:
                try:
                    o = obj.load(filepath, openpath = self.openpath)
                    name = o.data.get('id', None)
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
                if extension == '.parkobj':
                    filepath, filename = split(filepath)

                    # We assume that when the filename has more than 2 dots that the first part corresponds to the author id
                    if len(filename.split('.')) > 2:
                        author_id = filename.split('.')[0]
                else:
                    filepath = None

                if not self.current_palette == pal.orct:
                    o.switchPalette(self.current_palette)


                tab = wdg.objectTabSS(o, self, filepath, author_id)

                self.objectTabs.addTab(tab, name)
                self.objectTabs.setCurrentWidget(tab)

    def saveObject(self):
        widget = self.objectTabs.currentWidget()

        widget.saveObject(get_path = False)

    def saveObjectAt(self):
        widget = self.objectTabs.currentWidget()

        widget.saveObject(get_path = True)




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