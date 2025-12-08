# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""
from PyQt5.QtWidgets import QMainWindow, QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QApplication, QWidget, QSlider, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, \
    QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog, QGroupBox, QDial, QSpinBox, QTableWidget, \
    QTableWidgetItem, QHeaderView
from PyQt5 import uic, QtGui, QtCore

from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from enum import Enum
from pkgutil import get_data

from rctobject import palette as pal
from rctobject import constants as cts


class ToolCursors(QtGui.QCursor):
    def __init__(self, toolbox, zoom_factor, color=[0, 0, 0]):
        tool = toolbox.giveTool()
        brushsize = toolbox.giveBrushsize()
        shape = toolbox.giveBrushshape()

        if tool == Tools.EYEDROPPER or tool == Tools.FILL:
            super().__init__(QtCore.Qt.CrossCursor)
        else:
            size_x = int(brushsize*zoom_factor)+2
            if shape == BrushShapes.TILE:
                size_y = int((2*int((brushsize-1)/4)+1)*zoom_factor)+2
            else:
                size_y = size_x

            im = Image.new('RGBA', (size_x, size_y))
            draw = ImageDraw.Draw(im)
            draw.line([(0, 0), (size_x-1, 0), (size_x-1, size_y-1), (0, size_y-1), (0, 0)],
                      fill=(color[0], color[1], color[2], 255), width=1)

            im_qt = ImageQt(im)

            super().__init__(QtGui.QPixmap.fromImage(im_qt), hotX=1, hotY=1)


class ToolBoxWidget(QWidget):

    # define signals
    toolChanged = QtCore.pyqtSignal(object, name='toolChanged')

    def __init__(self):
        super().__init__()

        self.setFocusPolicy(QtCore.Qt.NoFocus)

        outer_container = QHBoxLayout()
        outer_container.setContentsMargins(0, 0, 0, 0)

        tool_button_widget = QWidget()
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        brush_widget = QGroupBox(title='Brush Options')
        brush_widget.setFlat(True)

        outer_container.addWidget(tool_button_widget)
        outer_container.addWidget(separator)
        outer_container.addWidget(brush_widget)

        self.setLayout(outer_container)

        container_tool_buttons = QGridLayout()
        container_tool_buttons.setContentsMargins(6, 10, 6, 10)

        self.tool_buttons = {}

        for tool in Tools:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setToolTip(tool.fullname)
            btn.setFocusPolicy(QtCore.Qt.NoFocus)

            icon = QtGui.QPixmap()
            icon.loadFromData(
                get_data("customwidgets", f'res/icon_{tool.fullname}.png'), 'png')
            btn.setIcon(QtGui.QIcon(icon))
            btn.setFixedSize(32, 32)
            btn.clicked.connect(lambda x, tool=tool: self.selectTool(tool))
            container_tool_buttons.addWidget(
                btn, int(tool.value/3), tool.value % 3)
            self.tool_buttons[tool] = btn

        tool_button_widget.setLayout(container_tool_buttons)
        self.tool = Tools.PEN
        self.last_tool = Tools.PEN
        self.tool_buttons[Tools.PEN].setChecked(True)

        container_lr = QHBoxLayout()
        container_lr.setContentsMargins(0, 0, 0, 0)
        brush_widget.setLayout(container_lr)

        container_btn = QGridLayout()
        container_spinboxes = QVBoxLayout()

        container_btn.setContentsMargins(0, 3, 0, 3)
        container_spinboxes.setContentsMargins(0, 3, 0, 3)
        container_spinboxes.setSpacing(2)

        brush_buttons = QWidget()
        spinboxes_widget = QWidget()

        brush_buttons.setLayout(container_btn)
        spinboxes_widget.setLayout(container_spinboxes)

        container_lr.addWidget(spinboxes_widget)
        container_lr.addWidget(brush_buttons)

        self.spinbox_brushsize = QSpinBox()
        self.spinbox_brushsize.setMaximum(32)
        self.spinbox_brushsize.setMinimum(1)
        self.spinbox_brushsize.setSingleStep(1)
        self.spinbox_brushsize.setToolTip("Brush Size")

        self.spinbox_brushsize.valueChanged.connect(self.setBrushsize)

        label = QLabel('Size')
        container_spinboxes.addWidget(label)
        container_spinboxes.addWidget(self.spinbox_brushsize)

        self.spinbox_airbrush_strength = QSpinBox()
        self.spinbox_airbrush_strength.setMaximum(6)
        self.spinbox_airbrush_strength.setMinimum(1)
        self.spinbox_airbrush_strength.setSingleStep(1)
        self.spinbox_airbrush_strength.setToolTip("Airbrush Strength")

        label = QLabel('Strength')
        container_spinboxes.addWidget(label)
        container_spinboxes.addWidget(self.spinbox_airbrush_strength)

        container_spinboxes.addStretch()

        self.brush_buttons = {}

        for brush in Brushes:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setToolTip(brush.fullname)
            icon = QtGui.QPixmap()
            icon.loadFromData(
                get_data("customwidgets", f'res/icon_{brush.fullname}.png'), 'png')
            btn.setIcon(QtGui.QIcon(icon))
            btn.setFixedSize(32, 32)
            btn.clicked.connect(lambda x, brush=brush: self.selectBrush(brush))
            self.brush_buttons[brush] = btn
            container_btn.addWidget(btn, 0, brush.value)

        self.brush = Brushes.SOLID
        self.brush_buttons[Brushes.SOLID].setChecked(True)

        self.shape_buttons = {}

        for shape in BrushShapes:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setToolTip(shape.fullname)
            icon = QtGui.QPixmap()
            icon.loadFromData(
                get_data("customwidgets", f'res/icon_{shape.fullname}.png'), 'png')
            btn.setIcon(QtGui.QIcon(icon))
            btn.setFixedSize(32, 32)
            btn.clicked.connect(
                lambda x, shape=shape: self.selectBrushshape(shape))
            self.shape_buttons[shape] = btn
            container_btn.addWidget(btn, 1, shape.value)

        self.shape = BrushShapes.SQUARE
        self.shape_buttons[BrushShapes.SQUARE].setChecked(True)

        self.brushsize = 1

    def selectTool(self, tool, store_last=False):
        if tool == self.tool:
            self.tool_buttons[tool].setChecked(True)
            return

        self.tool_buttons[tool].setChecked(True)
        self.tool_buttons[self.tool].setChecked(False)

        if store_last:
            self.last_tool = self.tool
        else:
            self.last_tool = tool

        self.tool = tool

        self.toolChanged.emit(self)

    def restoreTool(self):
        self.selectTool(self.last_tool)
        self.toolChanged.emit(self)

    def selectBrush(self, brush):
        if brush == self.brush:
            self.sender().setChecked(True)
            return

        self.brush_buttons[self.brush].setChecked(False)
        self.brush = brush

        self.toolChanged.emit(self)

    def selectBrushshape(self, shape):
        if shape == self.shape:
            self.sender().setChecked(True)
            return

        self.shape_buttons[self.shape].setChecked(False)
        self.shape = shape

        self.toolChanged.emit(self)

    def setBrushsize(self, val):
        self.brushsize = val

        self.toolChanged.emit(self)

    def giveTool(self):
        return self.tool

    def giveBrush(self):
        return self.brush

    def giveBrushsize(self):
        return self.brushsize

    def giveAirbrushStrength(self):
        return self.spinbox_airbrush_strength.value()**2*0.01

    def giveBrushshape(self):
        return self.shape


class Tools(Enum):
    PEN = 0, 'Draw'
    ERASER = 1, 'Erase'
    EYEDROPPER = 2, 'Eyedrop'
    BRIGHTNESS = 3, 'Brightness'
    REMAP = 4, 'Remap',
    FILL = 5, 'Fill'

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


class BrushShapes(Enum):
    SQUARE = 0, 'Square'
    ROUND = 1, 'Round'
    TILE = 2, 'Tile'

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
        self.buttons = []
        for i, shade in enumerate(color):
            border_shade = (0, 0, 0) if i > 3 else (230, 230, 230)
            b = ShadeButton(self, tuple(shade), border_shade=tuple(
                border_shade), color_name=colorname, index=i)
            b.clicked.connect(button_func)
            layout.insertWidget(0, b)
            self.buttons.append(b)
           # addWidget(b,-1)
        else:
            self.num_buttons = i+1

        self.checkbox = QCheckBox()
        self.checkbox.setToolTip(colorname)
        self.checkbox.setFixedSize(QtCore.QSize(13, 24))
        layout.addWidget(self.checkbox, 0)
        self.checkbox.setChecked(True)

        self.setLayout(layout)


class ShadeButton(QPushButton):
    def __init__(self, parent, shade, border_shade=(0, 0, 0), color_name=None, index=0):
        super().__init__(parent)
        self.color_name = color_name
        self.index = index
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
    def __init__(self, palette):
        super().__init__()
        container = QVBoxLayout()
        container.setContentsMargins(5, 5, 5, 5)
        container.setSpacing(0)
        self.setLayout(container)

        self.color_widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(3, 3, 3, 0)
        layout.addStretch()

        self.color_widget.setLayout(layout)
        # self.color_widget.setFixedSize(QtCore.QSize(
        #    240+int(first_remap)*16 + (int(second_remap) + int(third_remap))*3, 186))

        self.active_color_button = None

        self.bars = {}
        for colorname in palette.color_dict:
            if colorname == '1st Remap':
                bar = ColorBar(palette, colorname,
                               self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif colorname == '2nd Remap':
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif colorname == '3rd Remap':
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            else:
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 0)
                layout.insertWidget(0, bar)

            self.bars[colorname] = bar

        bar = ColorBar(palette, 'Sparkles',
                       self.shadeButtonClicked, 3)
        layout.insertWidget(-1, bar)
        bar.setVisible(False)
        self.bars['Sparkles'] = bar

        container.addWidget(self.color_widget)

        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(3, 3, 0, 0)

        button_widget.setLayout(button_layout)

        self.select_all = QPushButton(text='Select All')
        self.invert_all = QPushButton(text='Invert')
        self.activate_sparkles = QPushButton(text='Sparkles')
        self.activate_sparkles.setCheckable(True)
        self.activate_sparkles.setVisible(False)

        self.select_all.clicked.connect(self.clickSelectAll)
        self.invert_all.clicked.connect(self.clickInvert)
        self.activate_sparkles.clicked.connect(self.clickActivateSparkles)

        button_layout.addWidget(self.select_all, 0, QtCore.Qt.AlignLeft)
        button_layout.addWidget(self.invert_all, 0, QtCore.Qt.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(self.activate_sparkles,
                                0, QtCore.Qt.AlignRight)

        container.addWidget(button_widget, 0, QtCore.Qt.AlignLeft)

    def shadeButtonClicked(self):
        button = self.sender()
        if button is self.active_color_button:
            self.active_color_button = None
            return
        elif self.active_color_button:
            self.active_color_button.setChecked(False)

        self.active_color_button = button

    def clickSelectAll(self):
        for name, bar in self.bars.items():
            bar.checkbox.setChecked(True)

    def clickInvert(self):
        for name, bar in self.bars.items():
            bar.checkbox.setChecked(not bar.checkbox.isChecked())

    def clickActivateSparkles(self, value):
        self.bars['Sparkles'].setVisible(value)

    def setColor(self, color: str, shade_index: int):
        bar = self.bars[color]

        if shade_index < bar.num_buttons:
            btn = bar.buttons[shade_index]

            if not btn.isChecked():
                btn.click()

    def getColorIndices(self):
        if self.active_color_button:
            return self.active_color_button.color_name, self.active_color_button.index
        else:
            return None, None

    def selectedColors(self):
        ret = []
        for name, bar in self.bars.items():
            if bar.checkbox.isChecked() and bar.isVisible():
                ret.append(name)

        return ret

    def notSelectedColors(self):
        ret = []
        for name, bar in self.bars.items():
            if not bar.checkbox.isChecked():
                ret.append(name)

        return ret

    def giveActiveShade(self):
        if self.active_color_button:
            return self.active_color_button.shade
        else:
            return None

    def switchPalette(self, palette):
        layout = self.color_widget.layout()

        self.active_color_button = None

        # self.color_widget.setFixedSize(QtCore.QSize(
        #    240+int(first_remap)*16 + (int(second_remap) + int(third_remap))*3, 186))

        self.active_color_button = None

        for _, bar in self.bars.items():
            layout.removeWidget(bar)

        for colorname in palette.color_dict:
            if colorname == '1st Remap':
                bar = ColorBar(palette, colorname,
                               self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif colorname == '2nd Remap':
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            elif colorname == '3rd Remap':
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 3)
                layout.insertWidget(-1, bar)
            else:
                bar = ColorBar(palette, colorname, self.shadeButtonClicked, 0)
                layout.insertWidget(0, bar)

            self.bars[colorname] = bar

        bar = ColorBar(palette, 'Sparkles',
                       self.shadeButtonClicked, 3)
        layout.insertWidget(-1, bar)
        bar.setVisible(self.activate_sparkles.isChecked())
        self.bars['Sparkles'] = bar


class RemapColorSelectButton(QPushButton):
    # define signals
    colorChanged = QtCore.pyqtSignal(object, name='colorChanged')
    panelOpened = QtCore.pyqtSignal(name='panelOpened')

    def __init__(self, parent):
        super().__init__(parent)

        palette = pal.orct

        # QtCore.QCoreApplication.instance().centralwidget)
        self.select_panel = QWidget(parent=self.window())
        # self.select_panel.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.select_panel.setMinimumSize(QtCore.QSize(8*13, 4*13))

        container = QGridLayout()
        container.setSpacing(0)
        container.setContentsMargins(0, 0, 0, 0)
        self.select_panel.setLayout(container)

        self.active_color_button = None
        self.active_color = 'NoColor'
        self.buttons = {}
        for color_name, i in pal.remapColors().items():
            if i == -1:
                continue

            shade = palette.getRemapColor(color_name)[6]
            b = ShadeButton(self.select_panel, tuple(shade))
            b.clicked.connect(
                lambda x, color_name=color_name: self.colorButtonClicked(color_name))
            x = i % 8
            y = int(i/8)
            container.addWidget(b, y, x)
            self.buttons[color_name] = b

        self.select_panel.hide()

    def mousePressEvent(self, e):
        if self.select_panel.isVisible():

            self.select_panel.hide()
        else:
            x = self.select_panel.parent().mapFromGlobal(
                self.mapToGlobal(QtCore.QPoint(0, 0))).x()
            y = self.select_panel.parent().mapFromGlobal(
                self.mapToGlobal(QtCore.QPoint(0, 0))).y()

            self.select_panel.setGeometry(x+13, y-39, 8*13, 4*13)
            self.select_panel.show()

            self.panelOpened.emit()

        super().mousePressEvent(e)

    def colorButtonClicked(self, color_name):
        button = self.sender()
        if button is self.active_color_button:
            self.active_color_button = None
            self.active_color = 'NoColor'
            self.setStyleSheet("")
            color_name = 'NoColor'
        else:
            if self.active_color_button:
                self.active_color_button.setChecked(False)

            shade = button.shade
            self.setStyleSheet("QPushButton"
                               "{"
                               f"background-color :  rgb{shade};"
                               "}")

            self.active_color_button = button
            self.active_color = color_name

        self.select_panel.hide()
        self.colorChanged.emit(color_name)

    def setColor(self, color_name):
        if color_name == 'NoColor':
            if self.active_color_button:
                self.active_color_button.setChecked(False)
                self.hide()
        else:
            self.buttons[color_name].clicked.emit()
            self.buttons[color_name].setChecked(True)

    def currentColor(self):
        return self.active_color

    def hidePanel(self):
        if self.select_panel.isVisible():
            self.select_panel.hide()


class AnimationSpinBox(QSpinBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setEnabled(False)
        self.lineEdit().setStyleSheet('color: black; background-color: white;')
        self.lineEdit().setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        
        self.sequence = [0]

    def stepBy(self, steps):
        self.setValue(int(self.value()*2**steps))
        
class AnimationSequenceTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.currentCellChanged.connect(self.selectedCellChanged)
        
    def setRowCount(self, rows):
        super().setRowCount(rows)    
        
        for i in range(self.rowCount()):
            self.setRowHeight(i, 20)
            
    def setColumnCount(self, columns):
        super().setColumnCount(columns)    
        
        for i in range(self.columnCount()):
            self.setColumnWidth(i, 20)
            
    def selectedCellChanged(self, current_row, current_column, previous_row, previous_column):
        if previous_row != -1 and previous_column != -1:
            for col in range(self.columnCount()):
                if col != self.sequence[previous_row]:
                    row_item = self.takeItem(previous_row, col)
                        

            for row in range(self.rowCount()):
                col_item = self.item(row, previous_column)
                if col_item:
                    if previous_column == self.sequence[row]:
                        col_item.setBackground(QtCore.Qt.green)
                    else:
                        col_item.setBackground(QtCore.Qt.white)
        
        if current_row != -1 and current_column != -1:
            for col in range(self.columnCount()):
                if col != self.sequence[current_row]:
                    item = QTableWidgetItem()
                    self.setItem(current_row, col, item)
                    item.setBackground(QtCore.Qt.yellow)
                        

            for row in range(self.rowCount()):
                if current_column != self.sequence[row]:
                    item = QTableWidgetItem()
                    self.setItem(row, current_column, item)
                    item.setBackground(QtCore.Qt.yellow)
            
        
    def update(self, sequence):
        self.clearContents()
        
        self.sequence = sequence

        for row, column in enumerate(sequence):
            item = QTableWidgetItem()
            self.setItem(row, column, item)
            item.setBackground(QtCore.Qt.green)
        
        
        
        
class ButtonEventFilter(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() in [QtCore.QEvent.HoverEnter, QtCore.QEvent.HoverMove]:
            return True
        return False


class CursorComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(QtCore.QSize(61,41,))
        
        self.setIconSize(QtCore.QSize(32, 32))

        for cursor in cts.cursors:
            pixmap = self.createObjectCursorImage(cursor)
            icon = QtGui.QIcon()
            icon.addPixmap(pixmap)
            
            self.addItem(icon, '', userData=cursor)
        
    

    def createObjectCursorImage(self, cursor: str) -> QtGui.QImage:    
        image =QtGui.QImage(32, 32, QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)  # Start with a transparent background
        
        if cursor == 'CURSOR_ARROW':
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(
                get_data("customwidgets", f'res/cursor_arrow.png'), 'png')
            return pixmap
        elif cursor == 'CURSOR_HAND_POINT':
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(
                get_data("customwidgets", f'res/cursor_hand.png'), 'png')
            return pixmap
            
        bitmap_data = cts.cursors_data[cursor]
        # Map characters to colors
        for y in range(32):
            for x in range(32):
                char = bitmap_data[x + y*32]
                if char == 'X':
                    image.setPixelColor(x, y, QtGui.QColor(0,0,0,255))
                elif char == '.':
                    image.setPixelColor(x, y, QtGui.QColor(255,255,255,255))
                # Spaces are left transparent

        return QtGui.QPixmap.fromImage(image)
        
        