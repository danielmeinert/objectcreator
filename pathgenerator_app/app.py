# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 17:49:17 2022

@author: Daniel
"""

# app.py
import gui
import generate_path as gen
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys
import traceback
import ctypes

myappid = 'tols.objectmaker.pathgenerator.0.1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)



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


class PathGeneratorApp:
    def __init__(self):
        self.gui = gui.PathGeneratorUi()


def main():
    qapp = QApplication(sys.argv)
    app = PathGeneratorApp()
    qapp.exec_()


if __name__ == '__main__':
    main()
