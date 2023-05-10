# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:00:22 2022

@author: puvlh
"""
from PyQt5.QtWidgets import QMainWindow, QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog, QGroupBox, QDial
from PyQt5 import uic, QtGui, QtCore

from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from enum import Enum

from rctobject import palette as pal


class ToolCursors(QtGui.QCursor):
    def __init__(self, toolbox, zoom_factor):
        tool = toolbox.giveTool()
        brushsize = toolbox.giveBrushsize()
        brush = toolbox.giveBrush()
        
        if tool == Tools.EYEDROPPER:
            super().__init__(QtCore.Qt.CrossCursor)
        else:
            size = int(brushsize*zoom_factor)
            im = Image.new('RGBA', (size, size))
            draw = ImageDraw.Draw(im)
            draw.line([(0,0), (size,0), (size,size), (0,size), (0,0)], fill = (200,200,200,255), width =1)
            
            im_qt = ImageQt(im)
            
            super().__init__(QtGui.QPixmap.fromImage(im_qt))
            

class ToolBoxWidget(QWidget):

    #define signals
    toolChanged = QtCore.pyqtSignal(object, name='toolChanged')


    def __init__(self):
        super().__init__()

        outer_container = QHBoxLayout()
        outer_container.setContentsMargins(0,0,0,0)

        tool_button_widget = QWidget()
        seperator = QFrame()
        seperator.setFrameShape(QFrame.VLine)
        seperator.setFrameShadow(QFrame.Shadow.Sunken)
        brush_widget = QGroupBox(title='Brush Options')
        brush_widget.setFlat(True)


        outer_container.addWidget(tool_button_widget)
        outer_container.addWidget(seperator)
        outer_container.addWidget(brush_widget)

        self.setLayout(outer_container)

        container = QGridLayout()

        self.tool_buttons = {}

        for tool in Tools:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setText(tool.fullname)
            btn.clicked.connect(lambda x, tool = tool: self.selectTool(tool))
            container.addWidget(btn, tool.value % 3, int(tool.value/3))
            self.tool_buttons[tool] = btn


        tool_button_widget.setLayout(container)
        self.tool = Tools.PEN
        self.tool_buttons[Tools.PEN].setChecked(True)

        container_lr = QHBoxLayout()
        container_lr.setContentsMargins(0,0,0,0)
        container_btn = QVBoxLayout()
        brush_buttons = QWidget()

        self.dial_brushsize = QDial()
        self.dial_brushsize.setMaximum(10)
        self.dial_brushsize.setMinimum(1)
        self.dial_brushsize.setSingleStep(1)
        self.dial_brushsize.setPageStep(1)
        self.dial_brushsize.setTracking(False)
        self.dial_brushsize.setNotchesVisible(True)

        self.dial_brushsize.valueChanged.connect(self.setBrushsize)

        container_lr.addWidget(self.dial_brushsize)
        container_lr.addWidget(brush_buttons)

        brush_widget.setLayout(container_lr)

        self.brush_buttons = {}

        for brush in Brushes:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setText(brush.fullname)

            btn.clicked.connect(lambda x, brush = brush: self.selectBrush(brush))
            self.brush_buttons[brush] = btn
            container_btn.addWidget(btn)

        brush_buttons.setLayout(container_btn)
        self.brush = Brushes.SOLID
        self.brush_buttons[Brushes.SOLID].setChecked(True)

        self.brushsize = 1


    def selectTool(self, tool):
        if tool == self.tool:
            self.sender().setChecked(True)
            return

        self.tool_buttons[self.tool].setChecked(False)
        self.tool = tool
        
        self.toolChanged.emit(self)

    def selectBrush(self, brush):
        if brush == self.brush:
            self.sender().setChecked(True)
            return

        self.brush_buttons[self.brush].setChecked(False)
        self.brush = brush

    def setBrushsize(self, val):
        self.brushsize = val

        self.toolChanged.emit(self)


    def giveTool(self):
        return self.tool

    def giveBrush(self):
        return self.brush

    def giveBrushsize(self):
        return self.brushsize


class Tools(Enum):
        PEN = 0, 'Draw'
        ERASER = 1, 'Erase'
        EYEDROPPER = 2, 'Eyedrop'
        BRIGHTNESS = 3, 'Brightn.'
        REMAP = 4, 'Remap',
        FLOOD = 5, 'Fill'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value

class Brushes(Enum):
        SOLID = 0, 'Solid'
        AIRBRUSH = 1, 'Airbrush'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value



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
        self.checkbox.setChecked(True)

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
            elif second_remap and colorname == '2nd Remap':
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif third_remap and colorname == '3rd Remap':
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

    def notSelectedColors(self):
        ret = []
        for name, bar in self.bars.items():
            if not bar.checkbox.isChecked():
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
