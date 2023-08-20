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
from PyQt5 import uic, QtGui, QtCore, QtNetwork
from PIL import Image
from PIL.ImageQt import ImageQt
import traceback
import sys

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


import io, os
from os import getcwd
from os.path import splitext, split, abspath,join, exists
from json import load as jload
from json import dump as jdump
from enum import Enum
import requests

import customwidgets as cwdg
import widgets as wdg
import auxiliaries as aux

from rctobject import constants as cts
from rctobject import objects as obj
from rctobject import palette as pal

#import pyi_splash

# Update the text on the splash screen
#pyi_splash.update_text("Loading Object Creator")


VERSION = 'v0.1.3'


myappid = f'objectcreator.{VERSION}' # arbitrary string

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from ctypes import windll  # Only exists on Windows.
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindowUi(QMainWindow):
    def __init__(self, app_data_path, opening_objects = None):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/main_window.ui'), self)
        self.setWindowIcon(QtGui.QIcon(aux.resource_path("gui/icon.png")))
        self.setWindowTitle(f'Object Creator - {VERSION}')

        self.app_data_path = app_data_path
        self.loadSettings()
        self.bounding_boxes = aux.BoundingBoxes()
        self.symm_axes = aux.SymmetryAxes()


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

        self.button_lock = self.findChild(QToolButton, "toolButton_lock")
        self.button_lock.clicked.connect(self.lockClicked)
        self.button_push_sprite = self.findChild(QToolButton, "toolButton_pushSprite")
        self.button_push_sprite.clicked.connect(self.pushSprite)
        self.button_pull_sprite = self.findChild(QToolButton, "toolButton_pullSprite")
        self.button_pull_sprite.clicked.connect(self.pullSprite)

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

        self.actionSettings.triggered.connect(lambda x: self.changeSettings(update_widgets = True))

        self.actionBlackImport.triggered.connect(lambda x, mode=0: self.setCurrentImportColor(mode))
        self.actionWhiteImport.triggered.connect(lambda x, mode=1: self.setCurrentImportColor(mode))
        self.actionUpperLeftPixelImport.triggered.connect(lambda x, mode=2: self.setCurrentImportColor(mode))
        self.actionCustomColorImport.triggered.connect(lambda x, mode=3: self.setCurrentImportColor(mode))

        self.actionPaletteOpenRCT.triggered.connect(lambda x, palette=0: self.setCurrentPalette(palette))
        self.actionPaletteOld.triggered.connect(lambda x, palette=1: self.setCurrentPalette(palette))

        self.actionBlackBackground.triggered.connect(lambda x, mode=0: self.setCurrentBackgroundColor(mode))
        self.actionWhiteBackground.triggered.connect(lambda x, mode=1: self.setCurrentBackgroundColor(mode))
        self.actionCustomColorBackground.triggered.connect(lambda x, mode=2: self.setCurrentBackgroundColor(mode))

        self.actionCheckForUpdates.triggered.connect(self.checkForUpdates)
        self.actionAbout.triggered.connect(self.aboutPage)

        ### Left bar
        container = self.container_left_bar.layout()

        self.tool_widget = wdg.ToolWidgetSprite(self)
        container.addWidget(self.tool_widget)

        self.layer_widget = wdg.LayersWidget(self)
        container.addWidget(self.layer_widget)

        #function wrappers
        self.giveTool = self.tool_widget.toolbox.giveTool
        self.giveBrush = self.tool_widget.toolbox.giveBrush
        self.giveBrushsize = self.tool_widget.toolbox.giveBrushsize
        self.giveAirbrushStrength = self.tool_widget.toolbox.giveAirbrushStrength

        self.giveActiveShade = self.tool_widget.color_select_panel.giveActiveShade

        self.giveCurrentLayerIndex = self.layer_widget.layers_list.currentIndex

        #Load empty object if not started with objects

        if not opening_objects:
            self.newObject(cts.Type.SMALL)
        else:
            for filepath in opening_objects:
                self.loadObjectFromPath(filepath)

        self.show()
        self.checkForUpdates(silent = True)

    def checkForUpdates(self, silent = False):
        try:
            response = requests.get("https://api.github.com/repos/danielmeinert/objectcreator/releases/latest")
        except requests.exceptions.ConnectionError:
            return

        # check if there is a higher version on git
        git_version = response.json()['tag_name']

        if not versionCheck(git_version):
            if not silent:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("No update available")
                msg.setText(f"Object Creator {VERSION} is up to date!")
                msg.setStandardButtons(QMessageBox.Ok)

                msg.exec_()

            return

        url = response.json()['html_url']
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("New version available!")
        msg.setTextFormat(QtCore.Qt.RichText)

        msg.setText(f"Object Creator {git_version} is now available! <br> \
                Your version: {VERSION} <br> \
                <a href='{url}'>Click here to go to download page. </a> <br> <br> \
                Alternatively, would you like to update automatically? <br> \
                This only works if the program has been installed via the installer.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)


        reply = msg.exec_()

        # Only in the .exe program the updater can be used
        if reply == QMessageBox.Yes:
            #quit and run updater
            try:
                os.execl('updater.exe', 'updater.exe')
            except FileNotFoundError:
                return


    ### Internal methods

    def loadSettings(self):
        try:
            path = self.app_data_path
            self.settings = jload(fp=open(f'{path}/config.json'))
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

                self.settings['default_remaps'] = ['NoColor', 'NoColor', 'NoColor']
                self.settings['no_zip'] = False
                self.settings['clear_languages'] = False
                self.settings['version'] = '1.0'

                self.settings['transparency_color'] = 0
                self.settings['import_color'] = [0,0,0]
                self.settings['background_color'] = 0
                self.settings['background_color_custom'] = (0,0,0)
                self.settings['palette'] = 0
                self.settings['history_maximum'] = 5

                self.settings['small_scenery_defaults'] = {}

        self.openpath = self.settings['openpath']
        self.last_open_folder = self.settings.get('opendefault', None)
        self.setCurrentImportColor(self.settings['transparency_color'])
        self.setCurrentPalette(self.settings['palette'], update_widgets = False)
        self.setCurrentBackgroundColor(self.settings.get('background_color', 0), update_widgets = False)


    def saveSettings(self):
        path = self.app_data_path
        with open(f'{path}/config.json', mode='w') as file:
            jdump(obj=self.settings, fp=file, indent=2)

    def changeSettings(self, update_widgets = True):
        dialog = wdg.ChangeSettingsUi(self.settings)

        if dialog.exec():
            self.settings = dialog.ret

            self.openpath = self.settings['openpath']
            self.setCurrentImportColor(self.settings['transparency_color'])
            self.setCurrentPalette(self.settings['palette'], update_widgets = update_widgets)
            self.setCurrentBackgroundColor(self.settings['background_color'], update_widgets = update_widgets)

            self.saveSettings()

    def setCurrentImportColor(self, mode):
        if mode == 0:
            self.current_import_color = (0,0,0)
            self.actionBlackImport.setChecked(True)
            self.actionWhiteImport.setChecked(False)
            self.actionUpperLeftPixelImport.setChecked(False)
            self.actionCustomColorImport.setChecked(False)
        elif mode == 1:
            self.current_import_color = (255,255,255)
            self.actionBlackImport.setChecked(False)
            self.actionWhiteImport.setChecked(True)
            self.actionUpperLeftPixelImport.setChecked(False)
            self.actionCustomColorImport.setChecked(False)
        elif mode == 2:
            self.current_import_color = None
            self.actionBlackImport.setChecked(False)
            self.actionWhiteImport.setChecked(False)
            self.actionUpperLeftPixelImport.setChecked(True)
            self.actionCustomColor.setChecked(False)
        elif mode == 3:
            self.current_import_color = self.settings.get('import_color', (0,0,0))
            self.actionBlackImport.setChecked(False)
            self.actionWhiteImport.setChecked(False)
            self.actionUpperLeftPixelImport.setChecked(False)
            self.actionCustomColorImport.setChecked(True)

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
            self.tool_widget.color_select_panel.switchPalette(self.current_palette)
            for index in range(self.object_tabs.count()):
                tab = self.object_tabs.widget(index)
                tab.o.switchPalette(self.current_palette)
                tab.sprites_tab.updateAllViews()

    def setCurrentBackgroundColor(self, mode, update_widgets = True):
        if mode == 0:
            self.current_background_color = (0,0,0)
            self.actionBlackBackground.setChecked(True)
            self.actionWhiteBackground.setChecked(False)
            self.actionCustomColorBackground.setChecked(False)
        elif mode == 1:
            self.current_background_color = (255,255,255)
            self.actionBlackBackground.setChecked(False)
            self.actionWhiteBackground.setChecked(True)
            self.actionCustomColorBackground.setChecked(False)
        elif mode == 2:
            self.current_background_color = tuple(self.settings.get('background_color_custom', (0,0,0)))
            self.actionBlackBackground.setChecked(False)
            self.actionWhiteBackground.setChecked(False)
            self.actionCustomColorBackground.setChecked(True)

        if update_widgets:
            self.tool_widget.toolbox.toolChanged.emit(self.tool_widget.toolbox)
            for index in range(self.sprite_tabs.count()):
                tab = self.sprite_tabs.widget(index)
                tab.view.setStyleSheet("QLabel{"
                                      f"background-color :  rgb{self.current_background_color};"
                                      "}")

            for index in range(self.object_tabs.count()):
                tab = self.object_tabs.widget(index)
                tab.sprites_tab.sprite_view_main.setStyleSheet("QLabel{"
                                                               f"background-color :  rgb{self.current_background_color};"
                                                               "}")
                for _, preview in enumerate(tab.sprites_tab.sprite_preview):
                    preview.setStyleSheet("QLabel{"
                                          f"background-color :  rgb{self.current_background_color};"
                                          "}")


    def loadObjectFromPath(self, filepath):
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
            msg.setWindowTitle("Error Trapper")
            msg.setText("Failed to load object")
            msg.setInformativeText(str(traceback.format_exc()))
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


        object_tab = wdg.ObjectTab(o, self, filepath, author_id = author_id)

        sprite_tab = wdg.SpriteTab(self, object_tab)

        self.object_tabs.addTab(object_tab, name)
        self.object_tabs.setCurrentWidget(object_tab)
        self.sprite_tabs.addTab(sprite_tab,  f"{name} (locked)")
        self.sprite_tabs.setCurrentWidget(sprite_tab)

        self.last_open_folder = filepath

    ### Tab actions
    def changeObjectTab(self, index):
        object_tab = self.object_tabs.widget(index)
        if object_tab:
            if object_tab.locked:
                self.sprite_tabs.setCurrentIndex(self.sprite_tabs.indexOf(object_tab.locked_sprite_tab))
                self.button_lock.setChecked(True)
                self.button_pull_sprite.setEnabled(False)
                self.button_push_sprite.setEnabled(False)
            else:
                self.button_lock.setChecked(False)
                self.button_pull_sprite.setEnabled(True)
                self.button_push_sprite.setEnabled(True)

    def changeSpriteTab(self, index):
        sprite_tab = self.sprite_tabs.widget(index)

        if sprite_tab:
            sprite_tab.updateView()
            if sprite_tab.locked:
                self.object_tabs.setCurrentIndex(self.object_tabs.indexOf(sprite_tab.object_tab))
                self.button_lock.setChecked(True)
                self.button_pull_sprite.setEnabled(False)
                self.button_push_sprite.setEnabled(False)
                self.tool_widget.checkbox_all_views.setEnabled(True)
            else:
                self.button_lock.setChecked(False)
                self.button_pull_sprite.setEnabled(True)
                self.button_push_sprite.setEnabled(True)
                self.tool_widget.checkbox_all_views.setEnabled(False)
                self.tool_widget.checkbox_all_views.setChecked(False)


    def lockClicked(self):
        current_object_tab = self.object_tabs.currentWidget()
        current_sprite_tab = self.sprite_tabs.currentWidget()

        if current_object_tab is None or current_sprite_tab is None:
            return

        if self.button_lock.isChecked():
            name = self.object_tabs.tabText(self.object_tabs.currentIndex())

            if current_object_tab.locked:
                old_sprite_Tab = current_object_tab.locked_sprite_tab
                old_sprite_Tab.unlockObjectTab()
                self.sprite_tabs.setTabText(self.sprite_tabs.indexOf(old_sprite_Tab), f"Sprite {self.new_sprite_count}")
                self.new_sprite_count += 1

            self.pushSprite()

            current_object_tab.lockWithSpriteTab(current_sprite_tab)
            current_sprite_tab.lockWithObjectTab(current_object_tab)

            self.sprite_tabs.setTabText(self.sprite_tabs.currentIndex(), f"{name} (locked)")

            self.button_pull_sprite.setEnabled(False)
            self.button_push_sprite.setEnabled(False)
            self.tool_widget.checkbox_all_views.setEnabled(True)

        else:

            name = f'Sprite {self.new_sprite_count}'
            self.new_sprite_count += 1

            current_object_tab.unlockSpriteTab()
            current_sprite_tab.unlockObjectTab()

            self.sprite_tabs.setTabText(self.sprite_tabs.currentIndex(), f"{name}")

            self.button_pull_sprite.setEnabled(True)
            self.button_push_sprite.setEnabled(True)
            self.tool_widget.checkbox_all_views.setEnabled(False)
            self.tool_widget.checkbox_all_views.setChecked(False)


    def pushSprite(self):
        object_tab = self.object_tabs.currentWidget()
        sprite_tab = self.sprite_tabs.currentWidget()

        if object_tab:
            object_tab.setCurrentSprite(sprite_tab.sprite)

    def pullSprite(self):
        object_tab = self.object_tabs.currentWidget()
        sprite_tab = self.sprite_tabs.currentWidget()

        if sprite_tab:
            sprite_tab.setSprite(object_tab.giveCurrentMainViewSprite()[0])

    ### Menubar actions

    def newObject(self, obj_type = cts.Type.SMALL):
        o = obj.newEmpty(obj_type)
        name = f'Object {self.new_object_count}'
        self.new_object_count += 1

        if not self.current_palette == pal.orct:
            o.switchPalette(self.current_palette)

        object_tab = wdg.ObjectTab(o, self, author = self.settings['author'], author_id = self.settings['author_id'])
        sprite_tab = wdg.SpriteTab(self, object_tab)

        object_tab.lockWithSpriteTab(sprite_tab)

        object_tab.settings_tab.setDefaults()

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
                self.loadObjectFromPath(filepath)


    def saveObject(self):
        widget = self.object_tabs.currentWidget()

        if widget is not None:
            widget.saveObject(get_path = False)

    def saveObjectAt(self):
        widget = self.object_tabs.currentWidget()

        if widget is not None:
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


    def aboutPage(self):
        url = "https://github.com/danielmeinert/objectcreator"

        icon = QtGui.QPixmap(aux.resource_path("gui/icon.png"))

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About Object Creator")
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setIconPixmap(icon)

        msg.setText(f"Object Creator version {VERSION} <br> \
                If you want to give feedback or issue bugs, \
                visit the <a href='{url}'>github page. </a> <br> <br> \
                Copyright (c) 2023 Tolsimir <br> \
                The program 'Object Creator' is licensed under the GNU General Public License version 3.")
        msg.setStandardButtons(QMessageBox.Close)

        msg.exec_()


    ### Sprite Actions


    ### Keys & Events

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Alt:
            self.tool_widget.toolbox.selectTool(cwdg.Tools.EYEDROPPER)



    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_Alt:
            self.tool_widget.toolbox.restoreTool()

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
                self.loadObjectFromPath(filepath)

    def handleMessage(self, message):
        for filepath in message.split(' '):
            extension = splitext(filepath)[1].lower()

            if extension in ['.parkobj', '.dat', '.json']:
                self.loadObjectFromPath(filepath)
        else:
            self.activateWindow()



def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
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

def versionCheck(version):

    version = version[1:].split('.')
    version_this = VERSION[1:].split('.')

    for i in range(len(version_this),len(version)):
        version_this.append(0)

    for i, val in enumerate(version):

        if int(val) > int(version_this[i]):
            return True

    return False



### from https://stackoverflow.com/questions/8786136/pyqt-how-to-detect-and-close-ui-if-its-already-running

class SingleApplicationWithMessaging(QApplication):
    messageAvailable = QtCore.pyqtSignal(object)

    def __init__(self, argv, key):
        super().__init__(argv)
        # cleanup (only needed for unix)
        QtCore.QSharedMemory(key).attach()
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())


        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def isRunning(self):
        return self._running

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.messageAvailable.emit(
                socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print(socket.errorString())
                return False
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                print(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        return False



def main():
    # if not QApplication.instance():
    #     app = QApplication(sys.argv)
    # else:
    #     app = QApplication.instance()

    #pyi_splash.close()

    app = SingleApplicationWithMessaging(sys.argv, myappid)
    if app.isRunning():
        app.sendMessage(' '.join(sys.argv[1:]))
        sys.exit(1)

    app_data_path = join(os.environ['APPDATA'],'Object Creator')
    if not exists(app_data_path):
        os.makedirs(app_data_path)

    window = MainWindowUi(app_data_path= app_data_path, opening_objects= sys.argv[1:],)
    app.messageAvailable.connect(window.handleMessage)
    window.show()
    window.activateWindow()

    app.exec_()


    return main

if __name__ == '__main__':
    m = main()
