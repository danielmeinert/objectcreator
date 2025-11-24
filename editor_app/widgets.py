# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from operator import pos
from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QListWidgetItem, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PIL import Image, ImageGrab, ImageDraw
from PIL.ImageQt import ImageQt
from copy import copy, deepcopy
import io
import os.path
import sip
from os import getcwd
import numpy as np
from pkgutil import get_data


import auxiliaries as aux

from customwidgets import RemapColorSelectButton, ColorSelectWidget, ToolBoxWidget

import customwidgets as cwdg

from rctobject import constants as cts
from rctobject import sprites as spr
from rctobject import palette as pal
from rctobject import objects as obj

import widgetsSS
import widgetsLS


# Object Tab

class ObjectTab(QWidget):
    mainViewUpdated = QtCore.pyqtSignal()
    rotationChanged = QtCore.pyqtSignal(int)
    boundingBoxChanged = QtCore.pyqtSignal(
        [bool, object, tuple], [bool, object, tuple, tuple])
    symmAxesChanged = QtCore.pyqtSignal(bool, object, tuple)
    activeLayerRowChanged = QtCore.pyqtSignal(int)

    def __init__(self, o, main_window, filepath=None, author=None, author_id=None):
        super().__init__()

        self.o = o
        self.lastpath = filepath
        self.saved = False
        self.main_window = main_window

        self.locked = False
        self.locked_sprite_tab = False

        layout = QHBoxLayout()

        if o.object_type == obj.Type.SMALL:
            self.sprites_tab = widgetsSS.SpritesTab(o, self)
            self.settings_tab = widgetsSS.SettingsTab(
                o, self, self.sprites_tab, author, author_id)
        elif o.object_type == obj.Type.LARGE:
            self.sprites_tab = widgetsLS.SpritesTab(o, self)
            self.settings_tab = widgetsLS.SettingsTab(
                o, self, self.sprites_tab, author, author_id)
        else:
            raise RuntimeError('Object type not supported.')

        layout.addWidget(self.sprites_tab)
        layout.addWidget(self.settings_tab)

        self.setLayout(layout)

    def saveObject(self, get_path):

        name = self.o.data.get('id', '')
        if name == '':
            raise RuntimeError(
                'Cannot save object without id. Enter id first!')

        if get_path or not self.saved:
            if self.lastpath:
                folder = self.lastpath
                path = f"{self.lastpath}/{name}.parkobj"
            else:
                folder = self.main_window.settings.get('savedefault', '')
                if not folder:
                    folder = getcwd()
                path = f"{folder}/{name}.parkobj"

            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Object", path, "Parkobj Files (*.parkobj)")
            while filepath.endswith('.parkobj'):
                filepath = filepath[:-8]
            filepath, name = os.path.split(filepath)
        else:
            filepath = self.lastpath

        self.sprites_tab.save()
        self.settings_tab.save()

        if filepath:
            self.lastpath = filepath
            self.o.save(filepath, name=name,
                        no_zip=self.main_window.settings['no_zip'])
            self.saved = True

    def giveDummy(self):
        return self.settings_tab.giveDummy()

    def lockWithSpriteTab(self, locked_sprite_tab):
        if self.locked:
            self.unlockSpriteTab()

        self.locked = True
        self.sprites_tab.createLayers()
        
        self.locked_sprite_tab = locked_sprite_tab
        self.locked_sprite_tab.layerUpdated.connect(
            lambda: self.updateCurrentMainView(emit_signal=False))


    def unlockSpriteTab(self):
        self.locked = False
        self.locked_sprite_tab.layerUpdated.disconnect()
        #self.activeLayerRowChanged.disconnect()
        self.locked_sprite_tab = None

    def giveLayers(self):
        return self.sprites_tab.giveLayers()

    def giveCurrentMainViewSprite(self):
        return self.o.giveSprite()

    def updateCurrentMainView(self, emit_signal=True):
        self.sprites_tab.updateMainView(emit_signal)

    def addSpriteToHistoryAllViews(self):
        self.sprites_tab.addSpriteToHistoryAllViews()

    def setCurrentSprite(self, sprite):
        self.o.setSprite(sprite)
        self.updateCurrentMainView()

    def requestNumberOfLayers(self):
        return self.sprites_tab.requestNumberOfLayers()

    def setCurrentLayers(self, layers):
        self.sprites_tab.setCurrentLayers(layers)

    def colorRemapToAll(self, index, color_remap, selected_colors):
        if self.locked:
            self.sprites_tab.colorRemapToAll(
                index, color_remap, selected_colors)

    def colorChangeBrightnessAll(self, index, step, selected_colors):
        if self.locked:
            self.sprites_tab.colorChangeBrightnessAll(
                index, step, selected_colors)

    def colorRemoveAll(self, index, selected_colors):
        if self.locked:
            self.sprites_tab.colorRemoveAll(index, selected_colors)
            
    def colorInvertShadingAll(self, index, selected_colors):
        if self.locked:
            self.sprites_tab.colorInvertShadingAll(index, selected_colors)

# Sprites Tab


class SpriteTab(QWidget):
    layerUpdated = QtCore.pyqtSignal()
    layersChanged = QtCore.pyqtSignal()
    dummyChanged = QtCore.pyqtSignal()

    def __init__(self, main_window, object_tab=None, filepath=None):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/sprite.ui'), self)

        self.main_window = main_window

        # Canvas size

        self.canvas_width = 200
        self.canvas_height = 200

        self.base_x = int(self.canvas_width/2)
        self.base_y = self.canvas_height-70

        self.spinbox_width.setValue(self.canvas_width)
        self.spinbox_height.setValue(self.canvas_height)

        self.spinbox_width.valueChanged.connect(
            lambda x: self.canvasSizeChanged(left=(x-self.canvas_width)//2, right=(x-self.canvas_width)//2))
        self.spinbox_height.valueChanged.connect(
            lambda x: self.canvasSizeChanged(top=x-self.canvas_height))

        self.dummy_o = obj.newEmpty(obj.Type.SMALL)
        self.dummy_o.changeShape(self.dummy_o.Shape.QUARTER)
        self.dummy_o['properties']['height'] = 0
        self.dummy_coords = (0, 0)

        self.bounding_boxes_active = False
        self.symm_axes_active = False

        self.view.connectTab(self)
        self.view.setBackgroundBrush(QtCore.Qt.gray)

        self.lastpos = (0, 0)

        # Sprite zoom
        self.zoom_factor = 1
        self.slider_zoom.valueChanged.connect(self.zoomChanged)
        self.slider_zoom.valueChanged.connect(
            lambda x, toolbox=self.main_window.tool_widget.toolbox: self.toolChanged(toolbox))

        # Layers
        self.layers = SpriteLayerModel(1,1)

        self.layercount = 1

        self.locked = False
        self.object_tab = None
        
        if object_tab:
            self.lockWithObjectTab(object_tab)
        else:
            layer = SpriteLayer(spr.Sprite(None, palette=self.main_window.current_palette,
                                       transparent_color=self.main_window.current_import_color),
                            self.main_window, self.base_x, self.base_y, 0, 0, f'Layer {self.layercount}')
            self.layercount += 1

            self.layers.setItem(0, 0, layer)
            self.addLayerToCanvas(layer)

        self.protected_pixels = Image.new(
            '1', (self.canvas_width, self.canvas_height))

        self.lastpath = filepath
        self.saved = False
        self.main_window.tool_widget.toolbox.toolChanged.connect(
            self.toolChanged)
        self.toolChanged(self.main_window.tool_widget.toolbox)

        self.updateView()

    def lockWithObjectTab(self, object_tab):
        if object_tab:
            self.clearView()
            
            self.locked = True
            self.object_tab = object_tab
            object_tab.lockWithSpriteTab(self)
            self.object_tab.mainViewUpdated.connect(
                lambda: self.updateView(emit_signal=False))
            
            self.object_tab.rotationChanged.connect(self.updateLayersModel)
            self.object_tab.boundingBoxChanged.connect(
                self.boundingBoxesChanged)
            self.object_tab.symmAxesChanged.connect(self.symmAxesChanged)

            self.updateLayersModel()

            self.dummyChanged.emit()

        self.updateView()

    def unlockObjectTab(self):
        if self.locked:
            self.clearView()

            self.locked = False
            self.object_tab.mainViewUpdated.disconnect()
            self.object_tab.rotationChanged.disconnect(self.updateLayersModel)
            self.object_tab.boundingBoxChanged.disconnect(self.boundingBoxesChanged)
            self.object_tab.symmAxesChanged.disconnect(self.symmAxesChanged)

            self.layers = SpriteLayerModel(0,1)

            for row in range(self.object_tab.giveLayers().rowCount()):
                layer = self.object_tab.giveLayers().itemFromProxyRow(row)
                new_layer = SpriteLayer.fromLayer(layer)
                new_layer.setVisible(layer.isVisible())
                new_layer.setCheckState(layer.checkState())
                self.layers.insertProxyRow(row, new_layer)
                self.addLayerToCanvas(new_layer)

            self.layers.setActiveRow(self.object_tab.giveLayers().giveActiveProxyRow())

            self.dummy_o, self.dummy_coords = self.object_tab.giveDummy()
            self.dummyChanged.emit()

            self.object_tab = None
            self.layersChanged.emit()

    def giveDummy(self):
        if self.locked:
            return self.object_tab.giveDummy()
        else:
            return self.dummy_o, self.dummy_coords

    def canvasSizeChanged(self, left=0, right=0, top=0, bottom=0):
        width = self.canvas_width + left + right
        height = self.canvas_height + top + bottom

        if height is not None and height < self.canvas_height:
            # if height is smaller than the current canvas height, check if it is possible to resize

            dummy_o, dummy_coords = self.giveDummy()

            _, sprite_height = dummy_o.spriteBoundingBox()

            max_height = sprite_height + self.canvas_height - \
                self.base_y - dummy_coords[1]

            for row in range(self.giveLayers().rowCount()):
                layer = self.giveLayers().item(row)
                layer_height = -layer.sprite.y - layer.base_y + self.canvas_height

                max_height = max(max_height, layer_height)

            if height < max_height:
                self.spinbox_width.setValue(self.canvas_width)
                self.spinbox_height.setValue(self.canvas_height)
                return

        if width is not None and width < self.canvas_width:
            # if width is smaller than the current canvas width, check if it is possible to resize

            dummy_o, dummy_coords = self.giveDummy()

            sprite_width, _ = dummy_o.spriteBoundingBox()

            max_width = sprite_width + self.canvas_width - \
                self.base_x - dummy_coords[0]

            for row in range(self.giveLayers().rowCount()):
                layer = self.giveLayers().item(row)
                layer_width_left = -layer.sprite.x - layer.base_x + self.canvas_width
                layer_width_right = layer.sprite.image.size[0] + \
                    layer.sprite.x - layer.base_x + self.canvas_width

                max_width = max(max_width, layer_width_left, layer_width_right)

            if width < max_width:
                self.spinbox_width.setValue(self.canvas_width)
                self.spinbox_height.setValue(self.canvas_height)
                return

        if width:
            self.canvas_width = width
            self.spinbox_width.setValue(width)

        if height:
            self.canvas_height = height
            self.spinbox_height.setValue(height)

        self.setNewCanvasBase(x=self.base_x + left, y=self.base_y + top)

        self.view.updateCanvasSize()

        self.protected_pixels = Image.new(
            '1', (self.canvas_width, self.canvas_height))

    def setNewCanvasBase(self, x=None, y=None):
        if x:
            self.base_x = x
        if y:
            self.base_y = y

        for row in range(self.giveLayers().rowCount()):
            layer = self.giveLayers().item(row)
            layer.setBaseOffset(self.base_x, self.base_y)

        dummy_o, dummy_coords = self.giveDummy()

        _, coords = self.main_window.bounding_boxes.giveBackbox(
            dummy_o)
        self.view.layer_boundingbox.setOffset(
            coords[0]+self.base_x+dummy_coords[0], coords[1]+self.base_y+dummy_coords[1])

        _, coords = self.main_window.symm_axes.giveSymmAxes(dummy_o)
        self.view.layer_symm_axes.setOffset(
            coords[0]+self.base_x+dummy_coords[0], coords[1]+self.base_y+dummy_coords[1])

    def zoomChanged(self, val):
        self.view.scale(val/self.zoom_factor, val/self.zoom_factor)
        self.zoom_factor = val

    def toolChanged(self, toolbox):
        color = [255-c for c in self.main_window.current_background_color]
        cursor = cwdg.ToolCursors(toolbox, self.zoom_factor, color)
        self.view.viewport().setCursor(cursor)

    def boundingBoxesChanged(self, visible, backbox, coords):
        self.bounding_boxes_active = visible

        self.view.layer_boundingbox.setVisible(visible)

        image = ImageQt(backbox)

        pixmap = QtGui.QPixmap.fromImage(image)
        self.view.layer_boundingbox.setPixmap(pixmap)

        self.view.layer_boundingbox.setOffset(
            coords[0]+self.base_x, coords[1]+self.base_y)

        # adjust sprite margins
        width, height = backbox.size

        if coords[0]+self.base_x < 20:
            self.canvasSizeChanged(left=-coords[0]-self.base_x + 20)

        if coords[0]+self.base_x + width > self.canvas_width - 20:
            self.canvasSizeChanged(
                right=coords[0]+self.base_x + width + 20 - self.canvas_width)

        if coords[1]+self.base_y < 20:
            self.canvasSizeChanged(top=-coords[1]-self.base_y + 20)

        if coords[1]+self.base_y + height > self.canvas_height - 20:
            self.canvasSizeChanged(
                bottom=height + coords[1]+self.base_y - self.canvas_height + 20)

        self.dummyChanged.emit()

    def symmAxesChanged(self, visible, symm_axes, coords):
        self.symm_axes_active = visible

        self.view.layer_symm_axes.setVisible(visible)

        image = ImageQt(symm_axes)

        pixmap = QtGui.QPixmap.fromImage(image)
        self.view.layer_symm_axes.setPixmap(pixmap)
        self.view.layer_symm_axes.setOffset(
            coords[0]+self.base_x, coords[1]+self.base_y)

        self.dummyChanged.emit()

    def colorRemap(self, color_remap, selected_colors):
        layer = self.currentActiveLayer()
        layer.addSpriteToHistory()
        sprite = layer.sprite

        for color in selected_colors:
            sprite.remapColor(color, color_remap)

        self.updateView()

    def colorChangeBrightness(self, step, selected_colors):
        layer = self.currentActiveLayer()
        layer.addSpriteToHistory()
        sprite = layer.sprite

        sprite.changeBrightnessColor(step, selected_colors)

        self.updateView()

    def colorRemove(self, selected_colors):
        layer = self.currentActiveLayer()
        layer.addSpriteToHistory()
        sprite = layer.sprite

        sprite.removeColor(selected_colors)

        self.updateView()

    def colorInvertShading(self, selected_colors):
        layer = self.currentActiveLayer()
        layer.addSpriteToHistory()
        sprite = layer.sprite

        sprite.invertShadingColor(selected_colors)

        self.updateView()

    def changeSpriteOffset(self, direction: str):
        layer = self.currentActiveLayer()
        sprite = layer.sprite

        if direction == 'left':
            layer.setSpriteOffset(sprite.x - 1, sprite.y)
        elif direction == 'right':
            layer.setSpriteOffset(sprite.x + 1, sprite.y)
        elif direction == 'up':
            layer.setSpriteOffset(sprite.x, sprite.y - 1)
        elif direction == 'down':
            layer.setSpriteOffset(sprite.x, sprite.y + 1)
        elif direction == 'leftright':
            sprite.image = sprite.image.transpose(
                Image.FLIP_LEFT_RIGHT)
        elif direction == 'updown':
            sprite.image = sprite.image.transpose(
                Image.FLIP_TOP_BOTTOM)

        self.updateView()

    def draw(self, x, y, shade):
        layer = self.currentActiveLayer()
        sprite = layer.sprite
        canvas = Image.new('RGBA', (self.canvas_width, self.canvas_height))
        canvas_protect = Image.new(
            'RGBA', (self.canvas_width, self.canvas_height))

        coords = (layer.base_x+sprite.x,
                  layer.base_y+sprite.y)

        canvas.paste(sprite.image, coords, mask=sprite.image)
        canvas_protect.paste(sprite.image, coords, mask=sprite.image)

        brushsize = self.main_window.giveBrushsize()
        brushshape = self.main_window.giveBrushshape()

        draw = ImageDraw.Draw(canvas)
        if brushsize != 1:
            if brushshape == cwdg.BrushShapes.SQUARE:
                draw.rectangle(
                    [(x, y), (x+brushsize-1, y+brushsize-1)],  fill=shade)
            elif brushshape == cwdg.BrushShapes.ROUND:
                draw.ellipse(
                    [(x, y), (x+brushsize-1, y+brushsize-1)],  fill=shade)
            elif brushshape == cwdg.BrushShapes.TILE:
                x_mod = brushsize % 2
                y_mod = brushsize % 2

                for i in range(brushsize):
                    if i < int(brushsize/2):
                        draw.line([(x+i,  y-1+int(brushsize/2) - int((brushsize+1)/4)+y_mod - int(i/2)), (x+i,
                                  y-1+int(brushsize/2) - int((brushsize+1)/4)+y_mod + int(i/2))], fill=shade, width=1)
                    else:
                        draw.line(
                            [(x + i, y - 1 + int(brushsize / 2) - int((brushsize + 1) / 4) + y_mod -
                              int((brushsize - i - 1) / 2)),
                             (x + i, y - 1 + int(brushsize / 2) - int((brushsize + 1) / 4) + y_mod +
                              int((brushsize - i - 1) / 2))],
                            fill=shade, width=1)

        else:
            draw.point((x, y), shade)

        if self.lastpos != (x, y):
            x0, y0 = self.lastpos
            if brushsize % 2 == 0:
                x_mod = -1 if y > y0 else 0
                y_mod = -1 if x > x0 else 0
            else:
                x_mod = 0
                y_mod = 0

            if brushshape == cwdg.BrushShapes.TILE:
                brushsize = int(brushsize/2)

            draw.line([(int(x0+brushsize/2)+x_mod, int(y0+brushsize/2)+y_mod), (int(
                x+brushsize/2)+x_mod, int(y+brushsize/2)+y_mod)], fill=shade, width=brushsize)

            self.lastpos = (x, y)

        canvas.paste(canvas_protect, mask=self.protected_pixels)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -layer.base_x + bbox[0]
            y_offset = -layer.base_y + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        layer.setSpriteOffset(x_offset, y_offset)

        self.updateView()

    def erase(self, x, y):
        self.draw(x, y, (0, 0, 0, 0))

    def eyedrop(self, x, y):
        item = self.view.itemAt(self.view.mapFromScene(QtCore.QPointF(x, y)))
        
        if item in [self.view.layer_boundingbox, self.view.layer_symm_axes, self.view.background]:
            return
        
        r,g,b = item.pixmap().toImage().pixelColor(int(x - item.offset().x()), int(y - item.offset().y())).getRgb()[:3]

        indices = self.main_window.current_palette.giveShade(r, g, b, 255)

        if not indices:
            return

        self.main_window.tool_widget.color_select_panel.setColor(
            indices[0], indices[1])

    def overdraw(self, x, y):
        working_sprite = self.working_sprite
        layer = self.currentActiveLayer()
        sprite = layer.sprite
        canvas_mask = Image.new(
            '1', (self.canvas_width, self.canvas_height), color=1)
        canvas = Image.new('RGBA', (self.canvas_width, self.canvas_height))
        canvas_protect = Image.new(
            'RGBA', (self.canvas_width, self.canvas_height))

        coords = (layer.base_x+sprite.x,
                  layer.base_y+sprite.y)

        canvas.paste(working_sprite.image, coords, mask=working_sprite.image)
        canvas_protect.paste(sprite.image, coords, mask=sprite.image)

        brushsize = self.main_window.giveBrushsize()

        brushshape = self.main_window.giveBrushshape()

        draw = ImageDraw.Draw(canvas_mask)
        shade = 0
        if brushsize != 1:
            if brushshape == cwdg.BrushShapes.SQUARE:
                draw.rectangle(
                    [(x, y), (x+brushsize-1, y+brushsize-1)],  fill=shade)
            elif brushshape == cwdg.BrushShapes.ROUND:
                draw.ellipse(
                    [(x, y), (x+brushsize-1, y+brushsize-1)],  fill=shade)
            elif brushshape == cwdg.BrushShapes.TILE:
                x_mod = brushsize % 2
                y_mod = brushsize % 2

                for i in range(brushsize):
                    if i < int(brushsize/2):
                        draw.line([(x+i,  y-1+int(brushsize/2) - int((brushsize+1)/4)+y_mod - int(i/2)), (x+i,
                                  y-1+int(brushsize/2) - int((brushsize+1)/4)+y_mod + int(i/2))], fill=shade, width=1)
                    else:
                        draw.line(
                            [(x + i, y - 1 + int(brushsize / 2) - int((brushsize + 1) / 4) + y_mod -
                              int((brushsize - i - 1) / 2)),
                             (x + i, y - 1 + int(brushsize / 2) - int((brushsize + 1) / 4) + y_mod +
                              int((brushsize - i - 1) / 2))],
                            fill=shade, width=1)

        else:
            draw.point((x, y), shade)

        if self.lastpos != (x, y):
            x0, y0 = self.lastpos
            if brushsize % 2 == 0:
                x_mod = -1 if y > y0 else 0
                y_mod = -1 if x > x0 else 0
            else:
                x_mod = 0
                y_mod = 0

            if brushshape == cwdg.BrushShapes.TILE:
                brushsize = int(brushsize/2)

            draw.line([(int(x0+brushsize/2)+x_mod, int(y0+brushsize/2)+y_mod), (int(
                x+brushsize/2)+x_mod, int(y+brushsize/2)+y_mod)], fill=shade, width=brushsize)

            self.lastpos = (x, y)

        canvas_mask.paste(self.protected_pixels, mask=self.protected_pixels)

        canvas.paste(canvas_protect, mask=canvas_mask)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -layer.base_x + bbox[0]
            y_offset = -layer.base_y + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        layer.setSpriteOffset(x_offset, y_offset)

        self.updateView()

    def fill(self, x, y, shade):
        layer = self.currentActiveLayer()
        sprite = layer.sprite
        canvas = Image.new('RGBA', (self.canvas_width, self.canvas_height))
        canvas_protect = Image.new(
            'RGBA', (self.canvas_width, self.canvas_height))

        coords = (layer.base_x+sprite.x,
                  layer.base_y+sprite.y)

        canvas.paste(sprite.image, coords, mask=sprite.image)
        canvas_protect.paste(sprite.image, coords, mask=sprite.image)

        ImageDraw.floodfill(
            canvas, (x, y), (shade[0], shade[1], shade[2], 255))

        canvas.paste(canvas_protect, mask=self.protected_pixels)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -layer.base_x + bbox[0]
            y_offset = -layer.base_y + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        layer.setSpriteOffset(x_offset, y_offset)

        self.updateView()

    def generateProtectionMask(self):
        layer = self.currentActiveLayer()
        sprite = layer.sprite

        coords = (layer.base_x+sprite.x,
                  layer.base_y+sprite.y)

        self.protected_pixels = Image.new(
            '1', (self.canvas_width, self.canvas_height))
        self.protected_pixels.paste(sprite.giveProtectedPixelMask(
            self.main_window.tool_widget.color_select_panel.notSelectedColors()), coords)

        if self.main_window.giveBrush() == cwdg.Brushes.AIRBRUSH:
            strength = self.main_window.giveAirbrushStrength()
            noise_mask = Image.fromarray(np.random.choice(a=[True, False], size=(
                self.canvas_width, self.canvas_height), p=[1-strength, strength]).T)
            self.protected_pixels.paste(noise_mask, mask=noise_mask)

    def updateView(self, emit_signal=True):
        if self.currentActiveLayer() is not None:
            self.currentActiveLayer().updateLayer()
            if emit_signal:
                self.layerUpdated.emit()

    def updateLayersModel(self):
        if not self.locked:
            return

        self.clearView()
        for row in range(self.giveLayers().rowCount()):
            layer = self.giveLayers().giveLayerFromProxyRow(row)
            self.addLayerToCanvas(layer)

        self.layersChanged.emit()

    def updateLayersZValues(self):
        for row in range(self.giveLayers().rowCount()):
            layer = self.giveLayers().giveLayerFromProxyRow(row)
            item = layer.giveItem()

            item.setZValue(self.giveLayers().rowCount()-row)

        if self.locked:
            if self.object_tab.o.object_type == obj.Type.LARGE:
                active_layer = self.currentActiveLayer()
                if active_layer is not None:
                    item = active_layer.giveItem()
                    self.view.layer_boundingbox.setZValue(item.zValue()-1)

    def clearView(self):
        self.view.clearView()

    def addLayer(self, layer, pos=None):
        if self.locked:
            return
        
        if pos is None:
            pos = self.giveLayers().giveActiveProxyRow()

        if pos == -1:
            pos = 0
        
        self.giveLayers().insertProxyRow(pos, layer)
        self.addLayerToCanvas(layer)
        
        self.layersChanged.emit()
        

    def addLayerToCanvas(self, layer):
        
        layer.setBaseOffset(self.base_x, self.base_y)

        item = layer.giveItem()
        self.view.addLayerItem(item)
        self.updateLayersZValues()

        # adjust sprite margins
        width, height = layer.sprite.image.size

        if layer.base_x + layer.sprite.x < 20:
            self.canvasSizeChanged(left=-layer.base_x - layer.sprite.x + 20)

        if layer.base_x + width + layer.sprite.x > self.canvas_width - 20:
            self.canvasSizeChanged(
                right=layer.base_x + width + layer.sprite.x + 20 - self.canvas_width)

        if layer.base_y + layer.sprite.y < 20:
            self.canvasSizeChanged(top=-layer.base_y - layer.sprite.y + 20)

        if layer.base_y + height + layer.sprite.y > self.canvas_height - 20:
            self.canvasSizeChanged(
                bottom=height + layer.base_y + layer.sprite.y - self.canvas_height + 20)


    def newLayer(self, pos=None):
        if self.locked:
            return

        layer = SpriteLayer(spr.Sprite(None, palette=self.main_window.current_palette,
                                       transparent_color=self.main_window.current_import_color),
                            self.main_window, self.base_x, self.base_y, 0, 0, f'Layer {self.layercount}')
        self.layercount += 1

        self.addLayer(layer, pos)

        self.giveLayers().setActiveRowFromIndex(self.giveLayers().indexFromItem(layer))

        self.layersChanged.emit()

    def deleteLayer(self, index):
        if self.locked:
            return

        row = index.row()

        layer = self.giveLayers().takeProxyRow(row)[0]
        self.view.scene.removeItem(layer.item)
        del (layer)
        
        self.layersChanged.emit()

    def mergeLayer(self, index):
        if self.locked:
            return

        if (index.row() + 1) == self.giveLayers().rowCount():
            return

        layer_top = self.giveLayers().itemFromProxyIndex(index)
        layer_bottom = self.giveLayers().itemFromProxyRow(index.row()+1)

        layer_bottom.merge(layer_top)

        self.deleteLayer(index)

        self.layersChanged.emit()

    def moveLayer(self, index, direction):
        if self.locked:
            return

        layer = self.giveLayers().takeProxyRow(index.row())[0]

        if direction == 'up':
            self.giveLayers().insertProxyRow(index.row()-1, layer)

        elif direction == 'down':
            self.giveLayers().insertProxyRow(index.row()+1, layer)

        self.giveLayers().setActiveRowFromIndex(self.giveLayers().indexFromItem(layer))

        self.updateLayersZValues()

        self.layersChanged.emit()
    
    def setCurrentActiveLayerFromIndex(self, index):
        self.giveLayers().setActiveRowFromProxyIndex(index)

        if self.currentActiveLayer() is not None:
            if self.locked:
                if self.object_tab.o.object_type == obj.Type.LARGE:
                    item = self.currentActiveLayer().giveItem()
                    self.view.layer_boundingbox.setZValue(item.zValue())
                    


    def giveLayers(self):
        if self.locked:
            return self.object_tab.giveLayers()
        else:
            return self.layers

    def currentActiveLayer(self):
        return self.giveLayers().giveActiveLayer()

    def giveSprite(self):
        layer = self.currentActiveLayer()
        return layer.sprite

    def addSpriteToHistory(self):
        layer = self.currentActiveLayer()
        layer.addSpriteToHistory()

    def addSpriteToHistoryAllViews(self):
        if not self.locked:
            return

        self.object_tab.addSpriteToHistoryAllViews()

    def undo(self):
        layer = self.currentActiveLayer()
        layer.undo()

        self.updateView()

    def redo(self):
        layer = self.currentActiveLayer()
        layer.redo()

        self.updateView()

    def paste(self):
        self.addSpriteToHistory()
        if self.locked:
            self.object_tab.sprites_tab.pasteSpriteFromClipboard()
        else:
            if self.main_window.sprite_clipboard:
                for i in range(self.main_window.sprite_clipboard.rowCount()):
                    layer = self.main_window.sprite_clipboard.item(i, 0)
                    self.addLayer(layer)
                else:
                    self.giveLayers().setActiveRowFromIndex(self.giveLayers().indexFromItem(layer))

            else:
                image = ImageGrab.grabclipboard()
                if type(image) == list:
                    try:
                        image = Image.open(image[0])
                    except:
                        return

                image = image.convert('RGBA')

                if image:
                    selected_colors = self.main_window.tool_widget.color_select_panel.selectedColors()
                    

                    if self.main_window.current_import_offset_mode == 'bottom':
                        o, _ = self.giveDummy()
                        x, y, _ = o.size()
                        offset_y = (16*x+16*y)//2
                    else:
                        offset_y = 0

                    layer = SpriteLayer(
                        spr.Sprite(
                            image, palette=self.main_window.current_palette,
                            transparent_color=self.main_window.current_import_color,
                            selected_colors=selected_colors,
                            alpha_threshold=0,
                            offset=(0, offset_y),
                            auto_offset_mode=self.main_window.current_import_offset_mode),
                        self.main_window, self.base_x, self.base_y, 0, 0, f'Layer {self.layercount}')
                    self.layercount += 1

                    self.addLayer(layer)
                    self.giveLayers().setActiveRowFromIndex(
                        self.giveLayers().indexFromItem(layer))

    def copy(self):
        image = ImageQt(self.currentActiveLayer().sprite.image)
        pixmap = QtGui.QPixmap.fromImage(image)

        QApplication.clipboard().setPixmap(pixmap)
        layers = QtGui.QStandardItemModel()

        layers.insertRow(0, SpriteLayer.fromLayer(self.currentActiveLayer()))

        self.main_window.sprite_clipboard = layers
        self.main_window.sprite_clipboard_reset = False

    def switchPalette(self, palette):
        if self.locked:
            return

        for col in range(self.giveLayers().columnCount()):
            for row in range(self.giveLayers().rowCount()):
                layer = self.giveLayers().item(row, col)
                layer.sprite.switchPalette(palette)
                layer.updateLayer()


class SpriteViewWidget(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tab = None

        self.scene = QGraphicsScene()
        self.viewport().setMouseTracking(True)

        # Panning flags
        self.is_panning = False
        self.mouse_pressed = False
        self.space_pressed = False

        self.stored_cursor = QtCore.Qt.ArrowCursor

        self.slider_zoom = None
        self.mousepos = QtCore.QPoint(0, 0)

        self.setScene(self.scene)

    def connectTab(self, tab):
        self.tab = tab
        self.main_window = tab.main_window
        self.slider_zoom = tab.slider_zoom
        self.base_x = tab.base_x
        self.base_y = tab.base_y

        self.scene.setSceneRect(0, 0, tab.canvas_width, tab.canvas_height)

        self.setAuxiliaries()

    def addLayerItem(self, item):
        self.scene.addItem(item)

    def setAuxiliaries(self):
        self.background = QGraphicsRectItem(
            0, 0, self.tab.canvas_width, self.tab.canvas_height)
        self.background.setZValue(-2)
        brush = QtGui.QBrush(QtGui.QColor(self.tab.main_window.current_background_color[0],
                                          self.tab.main_window.current_background_color[1],
                                          self.tab.main_window.current_background_color[2]))
        self.background.setBrush(brush)
        self.scene.addItem(self.background)

        self.layer_boundingbox = QGraphicsPixmapItem()
        self.layer_boundingbox.setZValue(-1)
        self.layer_symm_axes = QGraphicsPixmapItem()
        self.layer_symm_axes.setZValue(100)

        self.scene.addItem(self.layer_boundingbox)
        self.scene.addItem(self.layer_symm_axes)
        
    def clearView(self):
        for item in self.scene.items():
            if item not in [self.background, self.layer_boundingbox, self.layer_symm_axes]:
                self.scene.removeItem(item)
        
    def updateCanvasSize(self):
        self.base_x = self.tab.base_x
        self.base_y = self.tab.base_y

        self.scene.setSceneRect(
            0, 0, self.tab.canvas_width, self.tab.canvas_height)

        self.scene.removeItem(self.background)

        self.background = QGraphicsRectItem(
            0, 0, self.tab.canvas_width, self.tab.canvas_height)
        self.background.setZValue(-2)
        brush = QtGui.QBrush(QtGui.QColor(self.tab.main_window.current_background_color[0],
                                          self.tab.main_window.current_background_color[1],
                                          self.tab.main_window.current_background_color[2]))
        self.background.setBrush(brush)
        self.scene.addItem(self.background)

    def updateBackgroundColor(self):
        brush = QtGui.QBrush(QtGui.QColor(self.tab.main_window.current_background_color[0],
                                          self.tab.main_window.current_background_color[1],
                                          self.tab.main_window.current_background_color[2]))
        self.background.setBrush(brush)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space and not self.mouse_pressed:
            self.is_panning = True
            self.space_pressed = True
            self.stored_cursor = self.viewport().cursor()
            self.viewport().setCursor(QtCore.Qt.OpenHandCursor)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.space_pressed = False
            if not self.mouse_pressed:
                self.is_panning = False
                self.viewport().setCursor(self.stored_cursor)

        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ControlModifier:
            zoom_factor = self.slider_zoom.value()
            if event.angleDelta().y() > 0 and zoom_factor != self.slider_zoom.maximum():
                self.slider_zoom.setValue(int(zoom_factor+1))
            elif event.angleDelta().y() < 0 and zoom_factor != self.slider_zoom.minimum():
                self.slider_zoom.setValue(int(zoom_factor-1))
        elif modifiers == QtCore.Qt.AltModifier:
            color, shade = self.main_window.tool_widget.color_select_panel.getColorIndices()
            if color:
                if event.angleDelta().x() > 0 and shade != 11:
                    self.main_window.tool_widget.color_select_panel.setColor(
                        color, shade+1)
                elif event.angleDelta().x() < 0 and shade != 0:
                    self.main_window.tool_widget.color_select_panel.setColor(
                        color, shade-1)
        elif modifiers == QtCore.Qt.ShiftModifier:
            toolbox = self.main_window.tool_widget.toolbox
            if event.angleDelta().y() > 0:
                toolbox.spinbox_brushsize.setValue(
                    toolbox.spinbox_brushsize.value()+1)
            elif event.angleDelta().y() < 0:
                toolbox.spinbox_brushsize.setValue(
                    toolbox.spinbox_brushsize.value()-1)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        screen_pos = self.mapToScene(event.localPos().toPoint())
        x = round(screen_pos.x())
        y = round(screen_pos.y())

        self.tab.lastpos = (x, y)

        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = True
            if self.is_panning:
                self.viewport().setCursor(QtCore.Qt.ClosedHandCursor)
                self._dragPos = event.pos()
                event.accept()
                return

            if self.main_window.giveTool() == cwdg.Tools.PEN:

                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()
                self.tab.draw(x, y, shade)
                return

            if self.main_window.giveTool() == cwdg.Tools.ERASER:

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()
                self.tab.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.EYEDROPPER:

                # since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x())
                y = int(screen_pos.y())

                self.tab.eyedrop(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.REMAP:

                color_remap = self.main_window.tool_widget.color_select_panel.getColorIndices()[
                    0]
                if not color_remap:
                    self.tab.working_sprite = None
                    return

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()
                self.tab.working_sprite = copy(self.tab.giveSprite())

                for color in self.main_window.tool_widget.color_select_panel.selectedColors():
                    self.tab.working_sprite.remapColor(color, color_remap)

                self.tab.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()
                self.tab.working_sprite = copy(self.tab.giveSprite())

                color_remap = self.main_window.tool_widget.color_select_panel.getColorIndices()[
                    0]

                for color in self.main_window.tool_widget.color_select_panel.selectedColors():
                    self.tab.working_sprite.changeBrightnessColor(1, color)

                self.tab.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.FILL:

                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                # since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x())
                y = int(screen_pos.y())

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()

                self.tab.fill(x, y, shade)
                return

        if event.button() == QtCore.Qt.RightButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()
                self.tab.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:

                self.tab.addSpriteToHistory()
                self.tab.generateProtectionMask()
                self.tab.working_sprite = copy(self.tab.giveSprite())

                color_remap = self.main_window.tool_widget.color_select_panel.getColorIndices()[
                    0]

                for color in self.main_window.tool_widget.color_select_panel.selectedColors():
                    self.tab.working_sprite.changeBrightnessColor(-1, color)

                self.tab.overdraw(x, y)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if self.mouse_pressed and self.is_panning:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            event.accept()
            return

        screen_pos = self.mapToScene(event.localPos().toPoint())
        x = round(screen_pos.x())
        y = round(screen_pos.y())

        x_display = -int(self.tab.base_x)+x
        y_display = -int(self.tab.base_y)+y

        self.tab.label_x.setText(f'X   {x_display}')
        self.tab.label_y.setText(f'Y   {y_display}')

        if event.buttons() == QtCore.Qt.LeftButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:
                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                self.tab.draw(x, y, shade)
                return

            if self.main_window.giveTool() == cwdg.Tools.ERASER:
                self.tab.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.EYEDROPPER:

                # since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x())
                y = int(screen_pos.y())

                self.tab.eyedrop(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.REMAP:
                if not self.tab.working_sprite:
                    return

                self.tab.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:
                if not self.tab.working_sprite:
                    return

                self.tab.overdraw(x, y)
                return

        if event.buttons() == QtCore.Qt.RightButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:
                self.tab.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:
                self.tab.overdraw(x, y)
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.space_pressed:
                self.viewport().setCursor(QtCore.Qt.OpenHandCursor)
            elif self.is_panning:
                self.is_panning = False
                self.viewport().setCursor(self.stored_cursor)
            self.mouse_pressed = False
        super().mouseReleaseEvent(event)

# Layers


class SpriteLayer(QtGui.QStandardItem):
    def __init__(self, sprite, main_window, base_x, base_y, offset_x=0, offset_y=0, name="Layer", parent=None):
        super().__init__(name)
        self.item = QGraphicsPixmapItem()

        self.main_window = main_window
        # self.base_x and self.base_y are the offset of the layer in the canvas
        self.base_x = base_x + offset_x
        self.base_y = base_y + offset_y  # base_x and base_y are the global base point
        # self.offset_x and self.offset_y are the offset of layer with respect to the canvas base point
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.visible = True

        self.sprite = sprite
        self.history = []
        self.history_redo = []

        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable |
                      QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        self.setCheckState(
            QtCore.Qt.CheckState.Checked if self.visible else QtCore.Qt.CheckState.Unchecked)

        self.updateLayer()

    @classmethod
    def fromLayer(cls, layer, new_name=None):
        sprite = deepcopy(layer.sprite)
        base_x = int(layer.base_x)
        base_y = int(layer.base_y)
        offset_x = int(layer.offset_x)
        offset_y = int(layer.offset_y)

        name = new_name if new_name else layer.text()

        return cls(sprite, layer.main_window, base_x, base_y, offset_x, offset_y, name)

    def isVisible(self):
        return self.visible

    def setVisible(self, val):
        self.visible = val
        self.item.setVisible(val)

    def addSpriteToHistory(self):
        sprite = copy(self.sprite)

        if len(self.history) == self.main_window.settings['history_maximum']:
            self.history.pop(0)

        self.history.append(sprite)
        self.history_redo = []

    def undo(self):
        if len(self.history) == 0:
            return

        sprite_new = self.history.pop(-1)

        self.history_redo.append(copy(self.sprite))

        self.sprite.image = sprite_new.image
        self.sprite.x = sprite_new.x
        self.sprite.y = sprite_new.y

        self.updateLayer()

    def redo(self):
        if len(self.history_redo) == 0:
            return

        sprite_new = self.history_redo.pop(-1)

        self.history.append(copy(self.sprite))

        self.sprite.image = sprite_new.image
        self.sprite.x = sprite_new.x
        self.sprite.y = sprite_new.y

        self.updateLayer()

    def setSprite(self, sprite):
        if sprite:
            self.sprite = sprite
            self.updateOffset()

            self.updateLayer()

    def merge(self, layer):
        self.addSpriteToHistory()

        sprite_top = copy(layer.sprite)
        self.sprite.merge(sprite_top, layer.base_x-self.base_x,
                          layer.base_y-self.base_y)

        self.updateOffset()
        self.updateLayer()

    def setSpriteOffset(self, x, y):
        self.sprite.x = x
        self.sprite.y = y

        self.item.setOffset(self.base_x + x, self.base_y + y)

    def updateOffset(self):
        self.item.setOffset(self.base_x + self.sprite.x,
                            self.base_y + self.sprite.y)

    def setBaseOffset(self, x, y):

        # x and y are the global base point
        self.base_x = x + self.offset_x
        self.base_y = y + self.offset_y

        self.updateOffset()

    def giveItem(self):
        if sip.isdeleted(self.item):
            self.item = QGraphicsPixmapItem()
            self.updateLayer()

        return self.item

    def updateLayer(self, sprite=None):
        if not sprite:
            sprite = self.sprite
        else:
            self.setSprite(sprite)

        image = ImageQt(sprite.image)

        pixmap = QtGui.QPixmap.fromImage(image)
        self.updateOffset()

        self.item.setPixmap(pixmap)


class SpriteLayerModel(QtGui.QStandardItemModel):
    activeRowChanged = QtCore.pyqtSignal(int)
    
    def __init__(self, rows, columns, orders=None, parent=None):
        super().__init__(rows, columns, parent)
        self.active_column = 0  # Active column in the fixed model
        self.active_row = 0     # Active row in the fixed model
        # List of orders for the columns, Default: Reversed Identity. It maps the rows of the proxy model to the rows of the original model for each column. Rows in the proxy model are inversed, i.e. the last row in the proxy model is the first row in the original model (when there is the identity).
        if orders is not None:
            self.orders = orders
        else:
            order = list(range(rows))
            order.reverse()
            self.orders = [order for _ in range(columns)]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Override data retrieval to return data from the active column."""
        if not index.isValid():
            return None

        # Only override for display role
        if role == QtCore.Qt.DisplayRole:
            # Get the row of the index

            return super().data(self.originalIndex(index), role)
        

        # Default behavior for other roles
        return super().data(index, role)

    def originalIndex(self, index):
        # Get the index in the original model for a given index in the proxy model
        if index.row() >= self.rowCount():
            return QtCore.QModelIndex()
        
        return self.index(self.orders[index.column()][index.row()], index.column())
    
    def originalRow(self, row, column = None):
        # For a given row and column from the proxy model, retrieve the row in the original model
        if column is None:
            column = self.active_column
        return self.orders[column][row]

    def proxyIndex(self, row, column):
        # For a given row and column from the original model, retrieve the index in the proxy model
        row = self.orders[column].index(row)
        return self.index(row, column)
    
    def item(self, row, column=None):
        # For a given row and column from the original model, retrieve the item in the original model
        if column is None:
            column = self.active_column
        
        return super().item(row, column)

    def itemFromProxyRow(self, row, column=None):
        # For a given row in the proxy model, retrieve the corresponding item in the original model
        if column is None:
            column = self.active_column
        original_row = self.orders[column][row]
        return super().item(original_row, column)
    
    def itemFromProxyIndex(self, index):
        # For a given index in the proxy model, retrieve the corresponding item in the original model
        original_row = self.orders[index.column()][index.row()]
        return self.item(original_row, index.column())
    
    def insertProxyRow(self, row, item):
        # For now this only works for single column models with reversed order
        self.insertRow(self.rowCount()-row, item)    
        
        self.orders[0].insert(0, len(self.orders[0]))   
        
    def takeProxyRow(self, row):
        # For now this only works for single column models with reversed order
        original_row = self.orders[0][row]
        item = self.takeRow(original_row)
        self.orders[0] = self.orders[0][1:]
        if original_row == self.active_row:
            if row >= len(self.orders[0]):
                self.active_row = self.orders[0][-1]
            else:
                self.active_row = self.orders[0][row]
                        
        

        return item
    
    def setActiveRow(self, row, emit_signal=True):
        self.active_row = row
        if emit_signal:
            self.activeRowChanged.emit(row)

    def setActiveRowFromIndex(self, index):
        self.active_row = index.row()
        self.activeRowChanged.emit(self.active_row)
    
    def setActiveRowFromProxyIndex(self, index):
        self.active_row = self.orders[index.column()][index.row()]
        self.activeRowChanged.emit(self.active_row)
        
    def setActiveRowFromItem(self, item):
        for col in range(self.columnCount()):
            for row in range(self.rowCount()):
                if self.item(row, col) == item:
                    self.active_row = row
                    self.active_column = col
                    self.activeRowChanged.emit(self.active_row)
                    return
        
    def setActiveColumn(self, column):
        self.active_column = column
        
    def giveActiveRow(self):
        return self.active_row
    
    def giveActiveProxyRow(self):
        return self.orders[self.active_column].index(self.active_row)
    
    def giveActiveColumn(self):
        return self.active_column
    
    def giveActiveLayer(self):
        return self.item(self.active_row, self.active_column)
    
    def giveCurrentProxyIndex(self):
        # Give the current active index in the proxy model
        return self.index(self.orders[self.active_column].index(self.active_row), self.active_column)
    
    def giveLayerFromProxyRow(self, row):
        # For a given row in the proxy model, retrieve the corresponding layer in the original model
        original_row = self.orders[self.active_column][row]
        return self.item(original_row, self.active_column)



class SpriteLayerListView(QtWidgets.QListView):
    checked = QtCore.pyqtSignal(QtCore.QModelIndex, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setItemDelegate(self.Delegate(self))

    class Delegate(QtWidgets.QStyledItemDelegate):
        def editorEvent(self, event, model, option, index):
            checked = index.data(QtCore.Qt.CheckStateRole)
            
            ret = QtWidgets.QStyledItemDelegate.editorEvent(
                self, event, model, option, index)
            if checked != index.data(QtCore.Qt.CheckStateRole):
                self.parent().checked.emit(index, bool(checked))
            return ret


class LayersWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/layers_sprites.ui'), self)

        self.main_window = main_window

        # Auxiliary
        self.button_bounding_box = self.findChild(
            QToolButton, "toolButton_boundingBox")
        self.button_symm_axes = self.findChild(
            QToolButton, "toolButton_symmAxes")
        self.button_rotate = self.findChild(
            QToolButton, "toolButton_rotate")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(aux.resource_path("gui/icon_Rotate.png")))
        self.button_rotate.setIcon(icon)

        self.button_bounding_box.clicked.connect(self.clickBoundingBox)
        self.button_symm_axes.clicked.connect(self.clickSymmAxes)
        self.button_rotate.clicked.connect(self.clickRotate)

        self.spin_box_clearance.valueChanged.connect(self.clearanceChanged)
        self.combo_box_shape.currentIndexChanged.connect(self.shapeChanged)

        # Sprite control buttons
        self.button_sprite_left = self.findChild(
            QToolButton, "toolButton_left")
        self.button_sprite_down = self.findChild(
            QToolButton, "toolButton_down")
        self.button_sprite_right = self.findChild(
            QToolButton, "toolButton_right")
        self.button_sprite_up = self.findChild(
            QToolButton, "toolButton_up")
        self.button_sprite_left_right = self.findChild(
            QToolButton, "toolButton_leftright")
        self.button_sprite_up_down = self.findChild(
            QToolButton, "toolButton_updown")

        self.button_sprite_left.clicked.connect(
            lambda x: self.clickSpriteControl('left'))
        self.button_sprite_down.clicked.connect(
            lambda x: self.clickSpriteControl('down'))
        self.button_sprite_right.clicked.connect(
            lambda x: self.clickSpriteControl('right'))
        self.button_sprite_up.clicked.connect(
            lambda x: self.clickSpriteControl('up'))
        self.button_sprite_left_right.clicked.connect(
            lambda x: self.clickSpriteControl('leftright'))
        self.button_sprite_up_down.clicked.connect(
            lambda x: self.clickSpriteControl('updown'))

        icon = QtGui.QPixmap()
        icon.loadFromData(
            get_data("customwidgets", 'res/icon_reflectionLR.png'), 'png')
        self.button_sprite_left_right.setIcon(QtGui.QIcon(icon))

        icon = QtGui.QPixmap()
        icon.loadFromData(
            get_data("customwidgets", 'res/icon_reflectionUD.png'), 'png')
        self.button_sprite_up_down.setIcon(QtGui.QIcon(icon))

        self.layers_list.checked.connect(self.layerChecked)

        self.button_new.clicked.connect(self.newLayer)
        self.button_merge.clicked.connect(self.mergeLayer)
        self.button_delete.clicked.connect(self.deleteLayer)
        self.button_up.clicked.connect(lambda: self.moveLayer('up'))
        self.button_down.clicked.connect(lambda: self.moveLayer('down'))

        self.updateList()
        
    def setActiveLayerRow(self, row):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            layers = widget.giveLayers()
            self.blockSignals(True)
            self.layers_list.setModelColumn(layers.giveActiveColumn())
            self.layers_list.setCurrentIndex(layers.giveCurrentProxyIndex())
            self.blockSignals(False)

    def updateList(self):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:            
            layers = widget.giveLayers() 

            self.layers_list.reset()
            self.layers_list.selectionModel().currentChanged.disconnect()
            self.layers_list.setModel(layers)
            
            self.layers_list.setModelColumn(layers.giveActiveColumn())
            
            #this is a hacky way to update the checkboxes, I'm fed up trying to find a better way (checkstaterole does not get the right index)
            for row in range(layers.rowCount()):
                item = layers.itemFromProxyRow(row)
                layers.item(row).setCheckState(QtCore.Qt.CheckState.Checked if item.visible else QtCore.Qt.CheckState.Unchecked)
            
            self.layers_list.setCurrentIndex(layers.giveCurrentProxyIndex())
            self.layers_list.selectionModel().currentChanged.connect(self.selectedLayerChanged)
        else:
            self.layers_list.setModel(QtGui.QStandardItemModel())
    

    def layerChecked(self, index, val):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            layers = widget.giveLayers()
            checked_state = QtCore.Qt.CheckState.Checked if not val else QtCore.Qt.CheckState.Unchecked
            
            original_row = layers.originalRow(index.row(), index.column())
            for col in range(layers.columnCount()):
                layers.item(original_row, col).setVisible(not val)

    def selectedLayerChanged(self, index):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget and index.isValid():
            
            widget.setCurrentActiveLayerFromIndex(index)

    def newLayer(self):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            widget.newLayer()

    def mergeLayer(self):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            if (self.layers_list.currentIndex().row() + 1) == widget.giveLayers().rowCount():
                return

            widget.mergeLayer(self.layers_list.currentIndex())

    def deleteLayer(self):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            if widget.giveLayers().rowCount() == 1:
                return

            widget.deleteLayer(self.layers_list.currentIndex())

    def moveLayer(self, direction):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            if (self.layers_list.currentIndex().row() + 1) == widget.giveLayers().rowCount() and direction == 'down':
                return
            if self.layers_list.currentIndex().row() == 0 and direction == 'up':
                return

            widget.moveLayer(self.layers_list.currentIndex(), direction)

    def clickSpriteControl(self, direction: str):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            widget.changeSpriteOffset(direction)

    def clickBoundingBox(self):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            dummy_o, dummy_coords = widget.giveDummy()

            backbox, coords = self.main_window.bounding_boxes.giveBackbox(
                dummy_o)
            widget.boundingBoxesChanged(
                self.button_bounding_box.isChecked(), backbox, (coords[0]+dummy_coords[0], coords[1]+dummy_coords[1]))

    def clickSymmAxes(self):
        widget = self.main_window.sprite_tabs.currentWidget()

        if widget:
            dummy_o, dummy_coords = widget.giveDummy()

            symm_axis, coords = self.main_window.symm_axes.giveSymmAxes(
                dummy_o)
            widget.symmAxesChanged(
                self.button_symm_axes.isChecked(), symm_axis, (coords[0]+dummy_coords[0], coords[1]+dummy_coords[1]))

    def clickRotate(self):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            if not widget.locked:
                widget.dummy_o.rotateObject()

                backbox, coords = self.main_window.bounding_boxes.giveBackbox(
                    widget.dummy_o)
                widget.boundingBoxesChanged(
                    self.button_bounding_box.isChecked(), backbox, coords)
                symm_axis, coords = self.main_window.symm_axes.giveSymmAxes(
                    widget.dummy_o)
                widget.symmAxesChanged(
                    self.button_symm_axes.isChecked(), symm_axis, coords)

    def clearanceChanged(self, value):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            if not widget.locked:
                widget.dummy_o['properties']['height'] = value*8

                backbox, coords = self.main_window.bounding_boxes.giveBackbox(
                    widget.dummy_o)
                widget.boundingBoxesChanged(
                    self.button_bounding_box.isChecked(), backbox, coords)

    def shapeChanged(self):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            if not widget.locked:
                value = self.combo_box_shape.currentIndex()
                if value == 0:
                    shape = obj.SmallScenery.Shape.QUARTER
                elif value == 1:
                    shape = obj.SmallScenery.Shape.HALF
                elif value == 2:
                    shape = obj.SmallScenery.Shape.THREEQ
                elif value == 3:
                    shape = obj.SmallScenery.Shape.FULL
                elif value == 4:
                    shape = obj.SmallScenery.Shape.FULLD
                elif value == 5:
                    shape = obj.SmallScenery.Shape.QUARTERD

                widget.dummy_o.changeShape(shape)

                backbox, coords = self.main_window.bounding_boxes.giveBackbox(
                    widget.dummy_o)
                widget.boundingBoxesChanged(
                    self.button_bounding_box.isChecked(), backbox, coords)
                symm_axis, coords = self.main_window.symm_axes.giveSymmAxes(
                    widget.dummy_o)
                widget.symmAxesChanged(
                    self.button_symm_axes.isChecked(), symm_axis, coords)

    def setDummyControls(self):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            dummy_o, dummy_coords = widget.giveDummy()
            if dummy_o:
                self.spin_box_clearance.setValue(
                    int(dummy_o['properties']['height']/8))
                try:
                    self.combo_box_shape.setCurrentIndex(dummy_o.shape.value)
                except AttributeError:
                    self.combo_box_shape.setCurrentIndex(
                        obj.SmallScenery.Shape.FULL.value)

    def setEnabledSpriteControls(self, val):
        widget = self.main_window.sprite_tabs.currentWidget()
        if widget:
            self.button_bounding_box.setChecked(widget.bounding_boxes_active)
            self.button_symm_axes.setChecked(widget.symm_axes_active)

        self.button_new.setEnabled(val)
        self.button_delete.setEnabled(val)
        self.button_merge.setEnabled(val)
        self.button_up.setEnabled(val)
        self.button_down.setEnabled(val)

        self.button_rotate.setEnabled(val)
        self.combo_box_shape.setEnabled(val)
        self.spin_box_clearance.setEnabled(val)
        self.label_clearance.setEnabled(val)


# Tools


class ToolWidgetSprite(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/tools_sprites.ui'), self)

        self.main_window = main_window

        # Tools
        widget_tool_box = self.findChild(QWidget, "widget_tool_box")
        self.toolbox = ToolBoxWidget()

        widget_tool_box.layout().addWidget(self.toolbox)

        # Color Panel
        self.widget_color_panel = self.findChild(
            QGroupBox, "groupBox_selectedColor")

        self.color_select_panel = ColorSelectWidget(
            self.main_window.current_palette)

        self.widget_color_panel.layout().addWidget(self.color_select_panel)

        # Color Manipulations
        self.checkbox_all_views = self.findChild(
            QCheckBox, "checkBox_allViews")

        self.button_remap_to = self.findChild(
            QPushButton, "pushButton_remapTo")
        self.combobox_remap_to_color = self.findChild(
            QComboBox, "comboBox_remapToColor")

        self.combobox_remap_to_color.addItems(
            list(self.main_window.current_palette.color_dict))
        self.combobox_remap_to_color.setCurrentIndex(
            self.main_window.current_palette.color_dict['1st Remap'])

        self.button_incr_brightness = self.findChild(
            QPushButton, "pushButton_incrBrightness")
        self.button_decr_brightness = self.findChild(
            QPushButton, "pushButton_decrBrightness")
        self.button_remove_color = self.findChild(
            QPushButton, "pushButton_deleteColor")
        self.button_invert_shading = self.findChild(
            QPushButton, "pushButton_invertShading")

        self.button_remap_to.clicked.connect(self.colorRemapTo)
        self.button_incr_brightness.clicked.connect(
            lambda x, step=1: self.colorChangeBrightness(step))
        self.button_decr_brightness.clicked.connect(
            lambda x, step=-1: self.colorChangeBrightness(step))
        self.button_remove_color.clicked.connect(self.colorRemove)
        self.button_invert_shading.clicked.connect(self.colorInvertShading
                                                   )

    # Color manipulations

    def colorRemapTo(self):
        color_remap = self.combobox_remap_to_color.currentText()
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()
            widget.colorRemapToAll(self.main_window.layer_widget.layers_list.currentIndex().row(), color_remap, selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()

            widget.colorRemap(color_remap, selected_colors)

    def colorChangeBrightness(self, step):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()
            widget.colorChangeBrightnessAll(self.main_window.layer_widget.layers_list.currentIndex().row(), step, selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()
            widget.colorChangeBrightness(step, selected_colors)

    def colorRemove(self):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()
            widget.colorRemoveAll(self.main_window.layer_widget.layers_list.currentIndex().row(), selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()
            widget.colorRemove(selected_colors)

    def colorInvertShading(self):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()
            widget.colorInvertShadingAll(self.main_window.layer_widget.layers_list.currentIndex().row(), selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()

            widget.colorInvertShading(selected_colors)

        # Settings window


class ChangeSettingsUi(QDialog):
    def __init__(self, settings):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/settings_window.ui'), self)

        self.setFixedSize(self.size())

        self.lineEdit_openpath.setText(settings.get('openpath'))
        self.lineEdit_saveDefault.setText(settings.get('savedefault'))
        self.lineEdit_openDefault.setText(settings.get('opendefault'))

        self.lineEdit_authorID.setText(settings.get('author_id'))
        self.lineEdit_author.setText(settings.get('author'))

        self.pushButton_changeOpenpath.clicked.connect(lambda x, sender=self.lineEdit_openpath:
                                                       self.clickChangeFolder(sender))
        self.pushButton_changeSaveDefault.clicked.connect(lambda x, sender=self.lineEdit_saveDefault:
                                                          self.clickChangeFolder(sender))
        self.pushButton_changeOpenDefault.clicked.connect(lambda x, sender=self.lineEdit_openDefault:
                                                          self.clickChangeFolder(sender))

        self.loadObjectSettings(settings)
        self.loadSpriteSettings(settings)
        self.loadSSSettings(settings)
        self.loadLSSettings(settings)

    def loadObjectSettings(self, settings):
        self.checkBox_nozip.setChecked(settings.get('no_zip', False))
        self.checkBox_clear_languages.setChecked(
            settings.get('clear_languages', False))

        self.doubleSpinBox_version.setValue(float(settings.get('version', 1)))

        self.pushButton_firstRemap.setColor(
            settings.get('default_remaps', ['NoColor', 'NoColor', 'NoColor'])[0])
        self.pushButton_secondRemap.setColor(
            settings.get('default_remaps', ['NoColor', 'NoColor', 'NoColor'])[1])
        self.pushButton_thirdRemap.setColor(
            settings.get('default_remaps', ['NoColor', 'NoColor', 'NoColor'])[2])

    def loadSpriteSettings(self, settings):
        self.comboBox_transparency_color.setCurrentIndex(
            settings.get('transparency_color', 0))
        self.spinBox_R_transparency.setValue(
            settings.get('import_color', (0, 0, 0))[0])
        self.spinBox_G_transparency.setValue(
            settings.get('import_color', (0, 0, 0))[1])
        self.spinBox_B_transparency.setValue(
            settings.get('import_color', (0, 0, 0))[2])

        self.comboBox_palette.setCurrentIndex(settings.get('palette', 0))
        self.spinBox_history_maximum.setValue(
            settings.get('history_maximum', 5))

        self.comboBox_background_color.setCurrentIndex(
            settings.get('background_color', 0))
        self.spinBox_R_background.setValue(
            settings.get('background_color_custom', (0, 0, 0))[0])
        self.spinBox_G_background.setValue(
            settings.get('background_color_custom', (0, 0, 0))[1])
        self.spinBox_B_background.setValue(
            settings.get('background_color_custom', (0, 0, 0))[2])

        self.comboBox_import_offset_mode.setCurrentIndex(
            settings.get('import_offset_mode', 0))

    def loadSSSettings(self, settings):
        for flag in cts.Jsmall_flags:
            checkbox = self.tab_SS_default.findChild(QCheckBox, f'{flag}_SS')
            if checkbox:
                checkbox.setChecked(settings.get(
                    'small_scenery_defaults', {}).get(flag, False))

        checkbox = self.tab_SS_default.findChild(QCheckBox, 'isTree_SS')
        checkbox.setChecked(settings.get(
            'small_scenery_defaults', {}).get('isTree', False))

        cursor_box = self.tab_SS_default.findChild(
            cwdg.CursorComboBox, "comboBox_cursor_SS")

        cursor_box.setCurrentIndex(cts.cursors.index(settings.get(
            'small_scenery_defaults', {}).get('cursor', 'CURSOR_BLANK')))

        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_price_SS")
        spinbox.setValue(
            int(settings.get('small_scenery_defaults', {}).get('price', 1)))
        spinbox = self.tab_SS_default.findChild(
            QSpinBox, "spinBox_removalPrice_SS")
        spinbox.setValue(
            int(settings.get('small_scenery_defaults', {}).get('removalPrice', 1)))

    def loadLSSettings(self, settings):
        for flag in ['allowSupportsAbove_LS', 'hasSupports_LS']:
            checkbox = self.tab_LS_default.findChild(QCheckBox, flag)
            checkbox.stateChanged.connect(lambda state, f=flag: self.tileFlagChanged(state, f))
            checkbox.setChecked(settings.get(
                                'large_scenery_defaults', {}).get(flag, False))
            self.tileFlagChanged(checkbox.checkState(), flag)

        cursor_box = self.tab_LS_default.findChild(
            cwdg.CursorComboBox, "comboBox_cursor_LS")
            
        cursor_box.setCurrentIndex(cts.cursors.index(settings.get(
            'large_scenery_defaults', {}).get('cursor', 'CURSOR_BLANK')))

        spinbox = self.tab_LS_default.findChild(QSpinBox, "spinBox_price_LS")
        spinbox.setValue(
            int(settings.get('large_scenery_defaults', {}).get('price', 1)))
        spinbox = self.tab_LS_default.findChild(
            QSpinBox, "spinBox_removalPrice_LS")
        spinbox.setValue(
            int(settings.get('large_scenery_defaults', {}).get('removalPrice', 1)))

    def clickChangeFolder(self, sender):
        directory = sender.text() if sender.text() != '' else "%USERPROFILE%/Documents/"
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", directory=directory)
        if folder:
            sender.setText(folder)
            
    def tileFlagChanged(self, state, flag):
        if flag == 'hasSupports_LS':
            self.tab_LS_default.findChild(QCheckBox, 'allowSupportsAbove_LS').setEnabled((state == QtCore.Qt.Checked))
            if state != QtCore.Qt.Checked:
                self.tab_LS_default.findChild(QCheckBox, 'allowSupportsAbove_LS').setChecked(False)

    def retrieveInputs(self):
        settings = {}

        settings['openpath'] = self.lineEdit_openpath.text()
        settings['savedefault'] = self.lineEdit_saveDefault.text()
        settings['opendefault'] = self.lineEdit_openDefault.text()
        settings['author'] = self.lineEdit_author.text()
        settings['author_id'] = self.lineEdit_authorID.text()

        settings['default_remaps'] = [
            self.pushButton_firstRemap.currentColor(),
            self.pushButton_secondRemap.currentColor(),
            self.pushButton_thirdRemap.currentColor()]

        settings['no_zip'] = self.checkBox_nozip.isChecked()
        settings['clear_languages'] = self.checkBox_clear_languages.isChecked()

        settings['version'] = self.doubleSpinBox_version.value()

        settings['transparency_color'] = self.comboBox_transparency_color.currentIndex()
        settings['import_color'] = [self.spinBox_R_transparency.value(
        ), self.spinBox_G_transparency.value(), self.spinBox_B_transparency.value()]
        settings['background_color'] = self.comboBox_background_color.currentIndex()
        settings['background_color_custom'] = (self.spinBox_R_background.value(
        ), self.spinBox_G_background.value(), self.spinBox_B_background.value())
        settings['palette'] = self.comboBox_palette.currentIndex()
        settings['history_maximum'] = self.spinBox_history_maximum.value()
        settings['import_offset_mode'] = self.comboBox_import_offset_mode.currentIndex()

        ss_defaults = {}
        for flag in cts.Jsmall_flags:
            checkbox = self.tab_SS_default.findChild(QCheckBox, f'{flag}_SS')
            if checkbox:
                ss_defaults[flag] = checkbox.isChecked()

        ss_defaults['isTree'] = self.isTree_SS.isChecked()

        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_price_SS")
        ss_defaults['price'] = spinbox.value()
        spinbox = self.tab_SS_default.findChild(
            QSpinBox, "spinBox_removalPrice_SS")
        ss_defaults['removalPrice'] = spinbox.value()

        ss_defaults['cursor'] = cts.cursors[self.tab_SS_default.findChild(
            cwdg.CursorComboBox, "comboBox_cursor_SS").currentIndex()]

        settings['small_scenery_defaults'] = ss_defaults

        ls_defaults = {}
        for flag in ['hasSupports_LS', 'allowSupportsAbove_LS']:
            checkbox = self.tab_LS_default.findChild(QCheckBox, flag)
            if checkbox:
                ls_defaults[flag] = checkbox.isChecked()

        spinbox = self.tab_LS_default.findChild(QSpinBox, "spinBox_price_LS")
        ls_defaults['price'] = spinbox.value()
        spinbox = self.tab_LS_default.findChild(
            QSpinBox, "spinBox_removalPrice_LS")
        ls_defaults['removalPrice'] = spinbox.value()

        ls_defaults['cursor'] = cts.cursors[self.tab_LS_default.findChild(
            cwdg.CursorComboBox, "comboBox_cursor_LS").currentIndex()]

        settings['large_scenery_defaults'] = ls_defaults

        return settings

    def accept(self):

        self.ret = self.retrieveInputs()
        super().accept()

class SpriteImportUi(QDialog):
    def __init__(self, layers_incoming, layers_object):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/sprite_import.ui'), self)

        self.setFixedSize(self.size())
        self.layers_incoming = layers_incoming
        self.layers_object = layers_object

        self.list_layers_incoming.setModel(layers_incoming)
        self.list_layers_incoming.setModelColumn(layers_incoming.giveActiveColumn())
        self.list_layers_object.setModel(layers_object)
        self.list_layers_object.setModelColumn(layers_object.giveActiveColumn())

    
        self.list_layers_incoming.setCurrentIndex(layers_incoming.giveCurrentProxyIndex())
        self.list_layers_object.setCurrentIndex(layers_object.giveCurrentProxyIndex())

    def accept(self):

        self.selected_incoming = QtGui.QStandardItemModel()

        for index in self.list_layers_incoming.selectedIndexes():
            layer = SpriteLayer.fromLayer(self.layers_incoming.itemFromProxyIndex(index))
            self.selected_incoming.appendRow(layer)

        # Selected target layer row in base model
        self.selected_row = self.list_layers_object.model().originalIndex(self.list_layers_object.currentIndex()).row()

        super().accept()
