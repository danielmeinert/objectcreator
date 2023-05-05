# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:00:22 2022

@author: puvlh
"""
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore

from rctobject import palette as pal


class ColorBar(QWidget):
    def __init__(self, palette, colorname, button_func, left_margin):
        super().__init__()
        self.setMinimumSize(QtCore.QSize(13+left_margin, 186))
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(left_margin, 0, 0, 0)

        color = palette.getColor(colorname)
        for i, shade in enumerate(color):
            border_shade = (0,0,0) if i > 3 else (230,230,230)
            b = ShadeButton(tuple(shade), border_shade = tuple(border_shade))
            b.clicked.connect(button_func)
            layout.insertWidget(0, b)
           # addWidget(b,-1)

        self.checkbox = QCheckBox()
        self.checkbox.setToolTip(colorname)
        self.checkbox.setFixedSize(QtCore.QSize(13, 24))
        layout.addWidget(self.checkbox, 0)

        self.setLayout(layout)


class ShadeButton(QPushButton):
    def __init__(self, shade, border_shade = (0,0,0)):
        super().__init__()
        self.setFixedSize(QtCore.QSize(13, 13))
        self.setCheckable(True)
        self.shade = shade

        self.setStyleSheet("QPushButton"
                           "{"
                           f"background-color :  rgb{shade};"
                           "}"
                           "QPushButton:pressed"
                           "{"
                           f"background-color : rgb{shade};"
                           "}"
                            "QPushButton:checked"
                            "{"
                            f"background-color : rgb{shade};"
                            f"border : 2px solid rgb{border_shade};"
                            "}"
                           )


class ColorSelectWidget(QWidget):
    def __init__(self, palette, first_remap: bool = False, second_remap: bool = False, third_remap: bool = False):
        super().__init__()
        container = QVBoxLayout()
        container.setContentsMargins(5,5,5,5)
        container.setSpacing(0)
        self.setLayout(container)

        self.color_widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(3,3,3,0)

        self.color_widget.setLayout(layout)
        self.color_widget.setFixedSize(QtCore.QSize(240+int(first_remap)*16 + (int(second_remap) + int(third_remap))*3, 186))


        self.active_color_button = None
        self.active_shade = None

        self.bars = {}
        for colorname in palette.color_dict:
            if colorname == '1st Remap':
                if first_remap:
                    bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                    layout.insertWidget(-1, bar)
            elif second_remap and colorname == 'Pink':
                colorname = '2nd Remap'
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif third_remap and colorname == 'Yellow':
                colorname = '3rd Remap'
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            else:
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 0)
                layout.insertWidget(0,bar)

            self.bars[colorname] = bar

        container.addWidget(self.color_widget)

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
            return
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

    def giveActiveShade(self):
        return self.active_shade
    
    def switchPalette(self, palette):
        layout = self.color_widget.layout()

        old_bar = self.bars.pop('1st Remap')
        layout.removeWidget(old_bar)
        bar = ColorBar(palette, '1st Remap', self.shadeButtonClicked, 3)
        layout.insertWidget(-1, bar)

        self.bars['1st Remap'] = bar



class RemapColorSelectWidget(QWidget):
    def __init__(self, palette ,parent, button_func, remap, window_button):
        super().__init__(parent=parent)

        self.active_color_button = None
        self.button = window_button

        self.setMinimumSize(QtCore.QSize(8*13,4*13))

        container = QGridLayout()
        container.setSpacing(0)
        container.setContentsMargins(0, 0, 0, 0)

        self.setLayout(container)

        for color_name, i in pal.remapColors().items():
            if i == -1:
                continue

            shade = palette.getRemapColor(color_name)[6]
            b = ShadeButton(tuple(shade))
            b.clicked.connect(lambda x, color_name = color_name, remap = remap, button_func = button_func: self.colorButtonClicked(color_name, remap, button_func))
            x = i % 8
            y = int(i/8)
            container.addWidget(b,y,x)

    def colorButtonClicked(self, color_name, remap, button_func):
        button = self.sender()
        if button is self.active_color_button:
            self.active_color_button = None
            button_func("NoColor", remap, self.button, None)
            self.hide()
            return

        if self.active_color_button:
            self.active_color_button.setChecked(False)

        self.active_color_button = button

        button_func(color_name, remap, self.button, button.shade)

        self.hide()
