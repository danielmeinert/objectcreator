# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget,QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
from customwidgets import colorSelectWidget
import widgets as wdg
import sys
import io
from os import getcwd
from os.path import splitext, split
from json import load as jload
from json import dump as jdump



import traceback

import editor as edi
from rctobject import constants as cts
from rctobject import objects as obj



class MainWindowUi(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        
        self.new_object_count = 1
        
        self.loadSettings()
        
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
        
        self.show()
        
    def loadSettings(self):
        try:
            self.settings = jload(fp=open('config.json'))
        except FileNotFoundError:
            self.settings = {}
            self.settings['openpath'] = obj.OPENRCTPATH
            self.settings['author'] = ''
            self.settings['author_id'] = ''
            self.settings['no_zip'] = False
            self.settings['version'] = '1.0'
            self.settings['import_color'] = None
            
        self.openpath = self.settings['openpath']

            
    def saveSettings(self):
        path = getcwd()
        with open(f'{path}/config.json', mode='w') as file:
            jdump(obj=self.settings, fp=file, indent=2)
        
        
    def newObject(self, obj_type = cts.Type.SMALL):
        o = obj.newEmpty(obj_type)
        name = f'Object {self.new_object_count}'
        self.new_object_count += 1
        
        tab = wdg.objectTabSS(o, author_id = self.settings['author_id'], settings = self.settings)
        
        self.objectTabs.addTab(tab, name)
        self.objectTabs.setCurrentWidget(tab)
    
    def closeObject(self, index):
        self.objectTabs.removeTab(index)
        
    def openObjectFile(self):
                
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Object", "", "All Object Type Files (*.parkobj *.DAT *.json);; Parkobj Files (*.parkobj);; DAT files (*.DAT);; JSON Files (*.json);; All Files (*.*)")

        if filepath:
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

            
            tab = wdg.objectTabSS(o, filepath, author_id, settings = self.settings)
        
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