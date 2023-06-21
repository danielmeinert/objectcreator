# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox, QWidget,QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
import io
from os.path import abspath,join

from pkgutil import get_data


from rctobject import constants as cts
from rctobject import objects as obj
from rctobject import palette as pal

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)



class BoundingBoxes():
    def __init__(self):
        self.loadBackboxes()

    def loadBackboxes(self):

        image = Image.open(resource_path("res/backbox_quarter.png"))
        self.backbox_quarter = [image, (-16,-7)]

        image = Image.open(resource_path("res/backbox_full.png"))
        self.backbox_full = [image, (-32,-15)]

        image_0 = Image.open(resource_path("res/backbox_half_0.png"))
        image_1 = Image.open(resource_path("res/backbox_half_1.png"))
        self.backbox_half = [[image_0, (-16,-15)],[image_1, (-16,-7)],[image_0, (-32,-7)],[image_1, (-32,-15)]]

        image_1 = Image.open(resource_path("res/backbox_diagonal_1.png"))
        self.backbox_diagonal = [[image_1, (-32,-15)],[self.backbox_quarter[0],(-16,-15)]]

        image_0 = Image.open(resource_path("res/backbox_three_quarter_0.png"))
        image_1 = Image.open(resource_path("res/backbox_three_quarter_2.png"))
        self.backbox_three_quarter = [[image_0, (-32,-15)],[self.backbox_half[0][0],(-16,-15)],[image_1, (-32,-15)],[self.backbox_half[1][0],(-32,-15)]]

        image = Image.open(resource_path("res/base_quarter.png"))
        self.base_quarter = [image, (-16,-7)]

        image = Image.open(resource_path("res/base_full.png"))
        self.base_full = [image, (-32,-15)]

        image_0 = Image.open(resource_path("res/base_half_0.png"))
        image_1 = Image.open(resource_path("res/base_half_1.png"))
        self.base_half = [[image_0, (-16,-15)],[image_1, (-16,-7)],[image_0, (-32,-7)],[image_1, (-32,-15)]]


        image_0 = Image.open(resource_path("res/base_diagonal_0.png"))
        image_1 = Image.open(resource_path("res/base_diagonal_1.png"))
        self.base_diagonal = [[image_1, (0,8)],[image_0, (16,0)]]

        image_0 = Image.open(resource_path("res/base_three_quarter_0.png"))
        image_1 = Image.open(resource_path("res/base_three_quarter_1.png"))
        image_2 = Image.open(resource_path("res/base_three_quarter_2.png"))
        image_3 = Image.open(resource_path("res/base_three_quarter_3.png"))
        self.base_three_quarter = [[image_0, (-32,0)],[image_1, (-32,0)],[image_2, (-32,8)],[image_3, (-32,0)]]


    def giveBackbox(self, o):
        object_type = o.object_type
        if object_type == cts.Type.SMALL:
            shape = o.shape
            h = int(o['properties']['height']/8)

            if shape == obj.SmallScenery.Shape.QUARTER or shape == obj.SmallScenery.Shape.QUARTERD:
                canvas = Image.new('RGBA', (32, 15 + h*8))

                for i in range(h+1):
                    if i == h:
                        canvas.paste(self.base_quarter[0], (0,h*8), self.base_quarter[0])
                    else:
                        canvas.paste(self.backbox_quarter[0], (0,i*8), self.backbox_quarter[0])

                return [canvas, (self.backbox_quarter[1][0], self.backbox_quarter[1][1]- 8*h)]

            elif shape == obj.SmallScenery.Shape.FULL:
                canvas = Image.new('RGBA', (64, 31 + h*8))

                for i in range(h+1):
                    if i == h:
                        canvas.paste(self.base_full[0], (0,h*8), self.base_full[0])
                    else:
                        canvas.paste(self.backbox_full[0], (0,i*8), self.backbox_full[0])

                return [canvas, (self.backbox_full[1][0], self.backbox_full[1][1]- 8*h)]

            elif shape == obj.SmallScenery.Shape.HALF:
                canvas = Image.new('RGBA', (64, 31 + h*8))

                rot = o.rotation

                for i in range(h+1):
                    if i == h:
                        canvas.paste(self.base_half[rot][0], (0,h*8), self.base_half[rot][0])
                    else:
                        canvas.paste(self.backbox_half[rot][0], (0,i*8), self.backbox_half[rot][0])

                return [canvas, (self.backbox_half[rot][1][0], self.backbox_half[rot][1][1]- 8*h)]

            elif shape == obj.SmallScenery.Shape.FULLD:
                canvas = Image.new('RGBA', (64, 31 + h*8))

                rot = o.rotation % 2

                for i in range(h+1):
                    if i == h:
                        canvas.paste(self.base_diagonal[rot][0], (0, self.base_diagonal[rot][1][1]+h*8), self.base_diagonal[rot][0])
                    else:
                        canvas.paste(self.backbox_diagonal[rot][0], (0,i*8), self.backbox_diagonal[rot][0])

                return [canvas, (self.backbox_diagonal[rot][1][0], self.backbox_diagonal[rot][1][1]- 8*h)]

            elif shape == obj.SmallScenery.Shape.THREEQ:
                canvas = Image.new('RGBA', (64, 31 + h*8))

                rot = o.rotation

                for i in range(h+1):
                    if i == h:
                        canvas.paste(self.base_three_quarter[rot][0], (0, self.base_three_quarter[rot][1][1] + h*8), self.base_three_quarter[rot][0])
                    else:
                        canvas.paste(self.backbox_three_quarter[rot][0], (0,i*8), self.backbox_three_quarter[rot][0])

                return [canvas, (self.backbox_three_quarter[rot][1][0], self.backbox_three_quarter[rot][1][1]- 8*h)]


class SymmetryAxes():
    def __init__(self):
        self.loadSymmAxes()

    def loadSymmAxes(self):
        image_0 = Image.open(resource_path("res/symm_quarter_0.png"))
        image_1 = Image.open(resource_path("res/symm_quarter_1.png"))
        self.symm_quarter = [[image_0, (-16,-7)],[image_1, (-16,-7)]]

        image_0 = Image.open(resource_path("res/symm_diag_quarter_0.png"))
        image_1 = Image.open(resource_path("res/symm_diag_quarter_1.png"))
        self.symm_quarter_diagonal = [[image_0, (-16,-7)],[image_1, (-16,-7)]]

        image_0 = Image.open(resource_path("res/symm_full_0.png"))
        image_1 = Image.open(resource_path("res/symm_full_1.png"))
        self.symm_full = [[image_0, (-32,-15)],[image_0, (-32,-15)]]

        image_0 = Image.open(resource_path("res/symm_half_0.png"))
        image_1 = Image.open(resource_path("res/symm_half_1.png"))
        self.symm_half = [[image_0, (-16,-15)],[image_1, (-16,-7)],[image_0, (-32,-7)],[image_1, (-32,-15)]]

        image_0 = Image.open(resource_path("res/symm_diagonal_0.png"))
        image_1 = Image.open(resource_path("res/symm_diagonal_1.png"))
        self.symm_diagonal = [[image_0, (-32,-15)],[image_1, (-32,-15)]]



    def giveSymmAxes(self, o):
        object_type = o.object_type
        if object_type == cts.Type.SMALL:
            shape = o.shape
            rot = o.rotation

            if shape == obj.SmallScenery.Shape.QUARTER:
                return self.symm_quarter[rot % 2]

            elif shape == obj.SmallScenery.Shape.QUARTERD:
                return self.symm_quarter_diagonal[rot % 2]

            elif shape == obj.SmallScenery.Shape.FULL:
                return self.symm_full[rot % 2]

            elif shape == obj.SmallScenery.Shape.HALF:
                return self.symm_half[rot]

            elif shape == obj.SmallScenery.Shape.THREEQ or shape == obj.SmallScenery.Shape.FULLD :
                return self.symm_diagonal[rot % 2]







