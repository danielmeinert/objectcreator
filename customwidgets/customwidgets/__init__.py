# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:00:22 2022

@author: puvlh
"""
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore

from rctobject import palette as pal


class colorBar(QWidget):
    def __init__(self, palette, colorname, button_func, left_margin):
        super().__init__()
        self.setMinimumSize(QtCore.QSize(13+left_margin, 186))
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(left_margin, 0, 0, 0)

        color = palette.getColor(colorname)
        for shade in color:
            b = shadeButton(tuple(shade))
            b.clicked.connect(button_func)
            layout.insertWidget(0, b)
           # addWidget(b,-1)

        self.checkbox = QCheckBox()
        self.checkbox.setToolTip(colorname)
        self.checkbox.setFixedSize(QtCore.QSize(13, 24))
        layout.addWidget(self.checkbox, 0)
        
        self.setLayout(layout)


class shadeButton(QPushButton):
    def __init__(self, shade):
        super().__init__()
        self.setFixedSize(QtCore.QSize(13, 13))
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
    def __init__(self, active_shade, palette, first_remap: bool = False, second_remap: bool = False, third_remap: bool = False):
        super().__init__()
        container = QVBoxLayout()
        container.setContentsMargins(5,5,5,5)
        container.setSpacing(0)
        self.setLayout(container)
        
        color_widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(3,3,3,0)

        color_widget.setLayout(layout)
        color_widget.setFixedSize(QtCore.QSize(240+int(first_remap)*16 + (int(second_remap) + int(third_remap))*3, 186))


        self.active_color_button = None
        self.active_shade = active_shade
        
        self.bars = {}
        for colorname in palette.color_dict:
            if colorname == '1st Remap':
                if first_remap: 
                    bar = colorBar(palette, colorname, self.shadeButtonClicked, 3)
                    layout.insertWidget(-1, bar)
            elif second_remap and colorname == 'Pink':
                colorname = '2nd Remap'
                bar = colorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif third_remap and colorname == 'Yellow':
                colorname = '3rd Remap'
                bar = colorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            else:
                bar = colorBar(palette, colorname, self.shadeButtonClicked, 0)
                layout.insertWidget(0,bar)
            
            self.bars[colorname] = bar
            
        container.addWidget(color_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(3,3,0,0)
        
        button_widget.setLayout(button_layout)
        
        self.select_all = QPushButton(text='Select All') 
        self.invert_all = QPushButton(text='Invert') 
        
        self.select_all.clicked.connect(self.clickSelectAll)
        self.invert_all.clicked.connect(self.clickInvert)
        
        button_layout.addWidget(self.select_all,0,QtCore.Qt.AlignLeft)
        button_layout.addWidget(self.invert_all,0,QtCore.Qt.AlignLeft)
        
        container.addWidget(button_widget,0,QtCore.Qt.AlignLeft)
        
    def shadeButtonClicked(self):
        button = self.sender()
        if button is self.active_color_button:
            self.active_color_button = None
            self.active_shade = None
        elif self.active_color_button:
            self.active_color_button.setChecked(False)

        self.active_color_button = button
        self.active_shade = button.shade
        
    def clickSelectAll(self):
        for name, bar in self.bars.items():
            bar.checkbox.setChecked(True)
            
    def clickInvert(self):
        for name, bar in self.bars.items():
            bar.checkbox.setChecked(not bar.checkbox.isChecked())

    def selectedColors(self):
        ret = []
        for name, bar in self.bars.items():
            if bar.checkbox.isChecked():
                ret.append(name)
        
        return ret
        
        
        