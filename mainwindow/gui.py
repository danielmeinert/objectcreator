# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget,QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
from customwidgets import colorSelectWidget
import widgets as wdg
import sys
import io
from os import getcwd

import editor as edi
from rctobject import constants as cts
from rctobject import objects as obj



class MainWindowUi(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        
        self.editor = edi.Editor()        
        
        
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
        
        self.show()
        
    def newObject(self, obj_type = cts.Type.SMALL):
        o, name = self.editor.newObject(obj_type)
        tab = QWidget()
        layout = QHBoxLayout()
        
        layout.addWidget(wdg.spritesTabSS(self.editor, o))
        layout.addWidget(wdg.settingsTabSS(self.editor, o))
        
        tab.setLayout(layout)
    
        self.objectTabs.addTab(tab, name)
        self.objectTabs.setCurrentWidget(tab)
    
    def closeObject(self, index):
        self.objectTabs.removeTab(index)
        self.editor.closeObject(self.objectTabs.currentIndex())
        
    def openObjectFile(self):
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Object", "", "Parkobj Files (*.parkobj);; DAT files (*.DAT);; JSON Files (*.json)")

        if filepath:
            o, name = self.editor.openObjectFile(filepath)
        
            tab = QWidget()
            layout = QHBoxLayout()
            
            layout.addWidget(wdg.spritesTabSS(self.editor, o))
            layout.addWidget(wdg.settingsTabSS(self.editor, o))
            
            tab.setLayout(layout)
        
            self.objectTabs.addTab(tab, name)
            self.objectTabs.setCurrentWidget(tab)
        
        
def main():
    # if not QApplication.instance():
    #     app = QApplication(sys.argv)
    # else:
    #     app = QApplication.instance()
   
    app = QApplication(sys.argv)

    main = MainWindowUi()
    main.show()
    app.exec_()

    #return main

if __name__ == '__main__':         
    m = main()