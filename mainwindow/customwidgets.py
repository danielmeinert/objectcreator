# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:00:22 2022

@author: puvlh
"""


from PyQt5.QtWidgets import QMainWindow,QVBoxLayout,QHBoxLayout, QApplication, QWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
import sys

from rctobject import palette as pal

class colorBar(QWidget):
    def __init__(self, palette, colorname, button_func):
        super().__init__()
        self.setMinimumSize(QtCore.QSize(13,186))
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        color = palette.getColor(colorname)
        for shade in color:
            b = shadeButton(tuple(shade))
            b.clicked.connect(button_func)
            layout.insertWidget(0, b)
           # addWidget(b,-1)
            
        checkbox = QCheckBox()
        checkbox.setToolTip(colorname)
        checkbox.setFixedSize(QtCore.QSize(13,24))
        layout.addWidget(checkbox,0)
        

        
class shadeButton(QPushButton):
    def __init__(self, shade):
        super().__init__()
        self.setFixedSize(QtCore.QSize(13,13))
        self.setCheckable(True)
        self.shade = shade

        self.setStyleSheet("QPushButton"
                             "{"
                             f"background-color :  rgb{shade}; border:none;"
                             "}"
                             "QPushButton:pressed"
                             "{"
                             f"background-color : rgb{shade}; border: none"
                             "}"
                             "QPushButton:checked"
                             "{"
                             f"background-color : rgb{shade};"
                             f"border : 2px solid black;"
                             "}"
                             )
  

 
class colorSelectWidget(QWidget):
    def __init__(self, palette, button_func):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        

        self.setLayout(layout)
        
        
        for colorname in palette.color_dict:
            bar = colorBar(palette, colorname, button_func)
            layout.addWidget(bar,0)

        
class Ui(QMainWindow):
    def __init__(self):
        super().__init__()
        w = QWidget()   
        l = QVBoxLayout()
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(0)
        w.setLayout(l)
        self.setCentralWidget(w)

        
        self.bar = colorSelectWidget(pal.orct, self.shadeButtonClicked)
        self.activeColorButton = None
        
        l.addWidget(self.bar)
        self.show()
        
    def shadeButtonClicked(self):
        button = self.sender()
        if button is self.activeColorButton:
            self.activeColorButton = None
            self.activeShade = None
        elif self.activeColorButton:
            self.activeColorButton.setChecked(False)
        
        self.activeColorButton = button   
        self.activeShade = button.shade
        
        
        
qapp = QApplication(sys.argv)
app = Ui()
        
        
        
        
        
        
        
        
        
        
        
        