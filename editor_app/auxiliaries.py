# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox, QWidget,QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
import io


from rctobject import constants as cts
from rctobject import objects as obj
from rctobject import palette as pal

import resources_rc



class BoundingBoxes():
    def __init__(self):
        self.loadBackboxes()

    def loadBackboxes(self):
        img = QtGui.QImage(":/images/res/backbox_quarter.png")
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image = Image.open(io.BytesIO(buffer.data()))
        self.backbox_quarter = [image, (-16,-7)]

        img = QtGui.QImage(":/images/res/backbox_full.png")
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image = Image.open(io.BytesIO(buffer.data()))
        self.backbox_full = [image, (-32,-7)]
        
        img = QtGui.QImage(":/images/res/backbox_half_0.png")
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image_0 = Image.open(io.BytesIO(buffer.data()))
        img = QtGui.QImage(":/images/res/backbox_half_1.png")
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image_1 = Image.open(io.BytesIO(buffer.data()))
        self.backbox_half = [[image_0, (-16,-7)],[image_1, (-16,1)],[image_0, (-32,1)],[image_1, (-32,-7)]]                
        
        img = QtGui.QImage(":/images/res/backbox_diagonal_0.png")
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image_0 = Image.open(io.BytesIO(buffer.data()))
        img = QtGui.QImage(":/images/res/backbox_diagonal_1.png")
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image_1 = Image.open(io.BytesIO(buffer.data()))
        self.backbox_diagonal = [[image_0, (-32,-7)],[image_1, (-32,-7)],[image_0, (-32,-7)],[image_1, (-32,-7)]]
        
        img = QtGui.QImage(":/images/res/base_quarter.png")
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image = Image.open(io.BytesIO(buffer.data()))
        self.base_quarter = [image, (-16,-7)]
        
        buffer.close()        
        
    def giveBackbox(self, o):
        object_type = o.object_type
        if object_type == cts.Type.SMALL:
            shape = o.shape
            h = int(o['properties']['height']/8)
            
            if shape == obj.SmallScenery.Shape.QUARTER or shape == obj.SmallScenery.Shape.QUARTERD: 
                if h == 0:
                    return self.base_quarter
                
                canvas = Image.new('RGBA', (32, 15 + h*8))
                
                for i in range(h):
                    canvas.paste(self.backbox_quarter[0], (0,i*8), self.backbox_quarter[0])
                    
                return [canvas, (self.backbox_quarter[1][0], self.backbox_quarter[1][1]- 8*h)]
            
            if shape == obj.SmallScenery.Shape.FULL: 
                canvas = Image.new('RGBA', (64, 31 + h*8))

                if h == 0:

                    return self.base_quarter
                
                
                for i in range(h):
                    canvas.paste(self.backbox_full[0], (0,i*8), self.backbox_full[0])
                    
                return [canvas, (self.backbox_full[1][0], self.backbox_full[1][1]- 8*h)]

                
        
        
        
        
        
        