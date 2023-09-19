# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""
from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image, ImageGrab, ImageDraw
from PIL.ImageQt import ImageQt
from copy import copy
import io
import os.path
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

# Object Tab


class ObjectTab(QWidget):
    def __init__(self, o, main_window, filepath=None, author=None, author_id=None):
        super().__init__()

        self.o = o
        self.lastpath = filepath
        self.saved = False
        self.main_window = main_window

        self.locked = False
        self.locked_sprite_tab = False

        layout = QHBoxLayout()

        if o.object_type == cts.Type.SMALL:
            self.sprites_tab = widgetsSS.SpritesTab(o, self)
            self.settings_tab = widgetsSS.SettingsTab(
                o, self, self.sprites_tab, author, author_id)
        else:
            raise RuntimeError('Object type not supported.')

        layout.addWidget(self.sprites_tab)
        layout.addWidget(self.settings_tab)

        self.setLayout(layout)

    def saveObject(self, get_path):

        name = self.o.data.get('id', '')

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

        if self.settings_tab.checkBox_remapCheck.isChecked():
            for path, sprite in self.o.sprites.items():
                if sprite.checkPrimaryColor():
                    self.o['properties']['hasPrimaryColour'] = True
                    break
            for path, sprite in self.o.sprites.items():
                if sprite.checkSecondaryColor():
                    self.o['properties']['hasSecondaryColour'] = True
                    break
            for path, sprite in self.o.sprites.items():
                if sprite.checkTertiaryColor():
                    self.o['properties']['hasTertiaryColour'] = True
                    break

        if filepath:
            self.lastpath = filepath
            self.o.save(filepath, name=name, no_zip=self.main_window.settings['no_zip'],
                        include_originalId=self.settings_tab.checkbox_keep_dat_id.isChecked())
            self.saved = True

    def lockWithSpriteTab(self, locked_sprite_tab):
        if self.locked:
            self.unlockSpriteTab()

        self.locked = True
        self.locked_sprite_tab = locked_sprite_tab

    def unlockSpriteTab(self):
        self.locked = False
        self.locked_sprite_tab = None

    def giveCurrentMainViewSprite(self):
        return self.o.giveSprite(return_index=True)

    def giveCurrentMainView(self, canvas_size=200, add_auxilaries=False):
        return self.sprites_tab.giveMainView(canvas_size, add_auxilaries)

    def updateCurrentMainView(self):
        self.sprites_tab.updateMainView()

    def setCurrentSprite(self, sprite):
        self.o.setSprite(sprite)
        self.updateCurrentMainView()

    def colorRemapToAll(self, color_remap, selected_colors):
        if self.locked:
            self.locked_sprite_tab.addSpriteToHistoryAllViews()

        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.remapColor(color, color_remap)

        self.sprites_tab.updateAllViews()

    def colorChangeBrightnessAll(self, step, selected_colors):
        if self.locked:
            self.locked_sprite_tab.addSpriteToHistoryAllViews()

        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.changeBrightnessColor(step, color)

        self.sprites_tab.updateAllViews()

    def colorRemoveAll(self, selected_colors):
        if self.locked:
            self.locked_sprite_tab.addSpriteToHistoryAllViews()

        for _, sprite in self.o.sprites.items():
            for color in selected_colors:
                sprite.removeColor(color)

        self.sprites_tab.updateAllViews()


# Sprites Tab

class SpriteTab(QWidget):
    def __init__(self, main_window, object_tab=None, filepath=None):
        super().__init__()
        uic.loadUi(aux.resource_path('gui/sprite.ui'), self)

        self.main_window = main_window

        self.scroll_area.connectTab(self)
        self.canvas_size = 200

        self.lastpos = (0, 0)

        self.view.setStyleSheet("QLabel{"
                                f"background-color :  rgb{self.main_window.current_background_color};"
                                "}")

        # Sprite zoom
        self.zoom_factor = 1
        self.slider_zoom.valueChanged.connect(self.zoomChanged)
        self.slider_zoom.valueChanged.connect(
            lambda x, toolbox=self.main_window.tool_widget.toolbox: self.toolChanged(toolbox))

        if object_tab:
            self.locked = True
            self.object_tab = object_tab
            object_tab.lockWithSpriteTab(self)

            self.sprite, _ = object_tab.giveCurrentMainViewSprite()
            o = object_tab.o
            self.history = []
            self.history_redo = []
            for sprite in o.sprites:
                self.history.append([])
                self.history_redo.append([])

        else:
            self.locked = False
            self.object_tab = None
            self.sprite = spr.Sprite(None)
            self.history = [[]]
            self.history_redo = [[]]

        self.protected_pixels = Image.new(
            '1', (self.canvas_size, self.canvas_size))

        self.lastpath = filepath
        self.saved = False
        self.main_window.tool_widget.toolbox.toolChanged.connect(
            self.toolChanged)
        self.toolChanged(self.main_window.tool_widget.toolbox)

        self.view.mousePressEvent = self.viewMousePressEvent
        self.view.mouseMoveEvent = self.viewMouseMoveEvent
        self.view.wheelEvent = self.viewWheelEvent
        self.view.keyPressEvent = self.viewKeyPressEvent

        self.updateView()

    def lockWithObjectTab(self, object_tab):
        if object_tab:
            self.locked = True
            self.object_tab = object_tab
            self.sprite, _ = object_tab.giveCurrentMainViewSprite()
            o = object_tab.o
            self.history = []
            self.history_redo = []
            for sprite in o.sprites:
                self.history.append([])
                self.history_redo.append([])

        self.updateView()

    def unlockObjectTab(self):
        if self.locked:
            self.sprite = copy(self.giveSprite()[0])
            index = self.giveSprite()[1]
            self.history = copy([self.history[index]])
            self.history_redo = copy([self.history_redo[index]])
            self.locked = False
            self.object_tab = None

    def setSprite(self, sprite):
        self.sprite = copy(sprite)

        self.updateView()

    def zoomChanged(self, val):
        self.zoom_factor = val

        self.updateView()

    def toolChanged(self, toolbox):
        color = [255-c for c in self.main_window.current_background_color]
        cursor = cwdg.ToolCursors(toolbox, self.zoom_factor, color)
        self.view.setCursor(cursor)

    def colorRemap(self, color_remap, selected_colors):
        self.addSpriteToHistory()
        sprite, _ = self.giveSprite()

        for color in selected_colors:
            sprite.remapColor(color, color_remap)

        self.updateView()

    def colorChangeBrightness(self, step, selected_colors):
        self.addSpriteToHistory()
        sprite, _ = self.giveSprite()

        sprite.changeBrightnessColor(step, selected_colors)

        self.updateView()

    def colorRemove(self, selected_colors):
        self.addSpriteToHistory()
        sprite, _ = self.giveSprite()

        sprite.removeColor(selected_colors)

        self.updateView()

    def clickSpriteControl(self, direction: str):
        sprite, _ = self.giveSprite()

        if direction == 'left':
            sprite.x -= 1
        elif direction == 'right':
            sprite.x += 1
        elif direction == 'up':
            sprite.y -= 1
        elif direction == 'down':
            sprite.y += 1
        elif direction == 'leftright':
            sprite.image = sprite.image.transpose(
                Image.FLIP_LEFT_RIGHT)
        elif direction == 'updown':
            sprite.image = sprite.image.transpose(
                Image.FLIP_TOP_BOTTOM)

        self.updateView()

    def draw(self, x, y, shade):
        sprite, _ = self.giveSprite()
        canvas = Image.new('RGBA', (self.canvas_size, self.canvas_size))
        canvas_protect = Image.new(
            'RGBA', (self.canvas_size, self.canvas_size))

        coords = (int(self.canvas_size/2)+sprite.x,
                  int(self.canvas_size*2/3)+sprite.y)

        canvas.paste(sprite.image, coords, mask=sprite.image)
        canvas_protect.paste(sprite.image, coords, mask=sprite.image)

        brushsize = self.main_window.giveBrushsize()

        draw = ImageDraw.Draw(canvas)
        if brushsize != 1:
            draw.rectangle(
                [(x, y), (x+brushsize-1, y+brushsize-1)],  fill=shade)
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

            draw.line([(int(x0+brushsize/2)+x_mod, int(y0+brushsize/2)+y_mod), (int(
                x+brushsize/2)+x_mod, int(y+brushsize/2)+y_mod)], fill=shade, width=brushsize)

            self.lastpos = (x, y)

        canvas.paste(canvas_protect, mask=self.protected_pixels)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -int(self.canvas_size/2) + bbox[0]
            y_offset = -int(self.canvas_size*2/3) + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        sprite.x = x_offset
        sprite.y = y_offset

        self.updateView()

    def erase(self, x, y):
        self.draw(x, y, (0, 0, 0, 0))

    def eyedrop(self, x, y):
        sprite, _ = self.giveSprite()

        coords = (int(self.canvas_size/2)+sprite.x,
                  int(self.canvas_size*2/3)+sprite.y)

        indices = sprite.giveShade((x-coords[0], y-coords[1]))

        if not indices:
            return

        self.main_window.tool_widget.color_select_panel.setColor(
            indices[0], indices[1])

    def overdraw(self, x, y):
        working_sprite = self.working_sprite
        sprite, _ = self.giveSprite()
        canvas_mask = Image.new(
            '1', (self.canvas_size, self.canvas_size), color=1)
        canvas = Image.new('RGBA', (self.canvas_size, self.canvas_size))
        canvas_protect = Image.new(
            'RGBA', (self.canvas_size, self.canvas_size))

        coords = (int(self.canvas_size/2)+sprite.x,
                  int(self.canvas_size*2/3)+sprite.y)

        canvas.paste(working_sprite.image, coords, mask=working_sprite.image)
        canvas_protect.paste(sprite.image, coords, mask=sprite.image)

        brushsize = self.main_window.giveBrushsize()

        draw = ImageDraw.Draw(canvas_mask)
        if brushsize != 1:
            draw.rectangle([(x, y), (x+brushsize-1, y+brushsize-1)],  fill=0)
        else:
            draw.point((x, y), 0)

        if self.lastpos != (x, y):
            x0, y0 = self.lastpos
            if brushsize % 2 == 0:
                x_mod = -1 if y > y0 else 0
                y_mod = -1 if x > x0 else 0
            else:
                x_mod = 0
                y_mod = 0

            draw.line([(int(x0+brushsize/2)+x_mod, int(y0+brushsize/2)+y_mod),
                      (int(x+brushsize/2)+x_mod, int(y+brushsize/2)+y_mod)], fill=0, width=brushsize)

            self.lastpos = (x, y)

        canvas_mask.paste(self.protected_pixels, mask=self.protected_pixels)

        canvas.paste(canvas_protect, mask=canvas_mask)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -int(self.canvas_size/2) + bbox[0]
            y_offset = -int(self.canvas_size*2/3) + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        sprite.x = x_offset
        sprite.y = y_offset

        self.updateView()

    def fill(self, x, y, shade):
        sprite, _ = self.giveSprite()
        canvas = Image.new('RGBA', (self.canvas_size, self.canvas_size))
        canvas_protect = Image.new(
            'RGBA', (self.canvas_size, self.canvas_size))

        coords = (int(self.canvas_size/2)+sprite.x,
                  int(self.canvas_size*2/3)+sprite.y)

        canvas.paste(sprite.image, coords, mask=sprite.image)
        canvas_protect.paste(sprite.image, coords, mask=sprite.image)

        ImageDraw.floodfill(
            canvas, (x, y), (shade[0], shade[1], shade[2], 255))

        canvas.paste(canvas_protect, mask=self.protected_pixels)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -int(self.canvas_size/2) + bbox[0]
            y_offset = -int(self.canvas_size*2/3) + bbox[1]
        else:
            x_offset = 0
            y_offset = 0

        sprite.image = canvas
        sprite.x = x_offset
        sprite.y = y_offset

        self.updateView()

    def generateProtectionMask(self):
        sprite, _ = self.giveSprite()

        coords = (int(self.canvas_size/2)+sprite.x,
                  int(self.canvas_size*2/3)+sprite.y)

        self.protected_pixels = Image.new(
            '1', (self.canvas_size, self.canvas_size))
        self.protected_pixels.paste(sprite.giveProtectedPixelMask(
            self.main_window.tool_widget.color_select_panel.notSelectedColors()), coords)

        if self.main_window.giveBrush() == cwdg.Brushes.AIRBRUSH:
            strength = self.main_window.giveAirbrushStrength()
            noise_mask = Image.fromarray(np.random.choice(a=[True, False], size=(
                self.canvas_size, self.canvas_size), p=[1-strength, strength]).T)
            self.protected_pixels.paste(noise_mask, mask=noise_mask)

    def viewKeyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Up:
            self.clickSpriteControl('up')

    def viewMousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # Control modifier = sprite control, dealt with by parent
        if modifiers == QtCore.Qt.ControlModifier:
            event.ignore()
            return

        screen_pos = event.localPos()
        x = round(screen_pos.x()/self.zoom_factor)
        y = round(screen_pos.y()/self.zoom_factor)

        self.lastpos = (x, y)

        if event.button() == QtCore.Qt.LeftButton:
            if self.main_window.giveTool() == cwdg.Tools.PEN:

                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.draw(x, y, shade)
                return

            if self.main_window.giveTool() == cwdg.Tools.ERASER:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.EYEDROPPER:

                # since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x()/self.zoom_factor)
                y = int(screen_pos.y()/self.zoom_factor)

                self.eyedrop(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.REMAP:

                color_remap = self.main_window.tool_widget.color_select_panel.getColorIndices()[
                    0]
                if not color_remap:
                    self.working_sprite = None
                    return

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.working_sprite = copy(self.giveSprite()[0])

                for color in self.main_window.tool_widget.color_select_panel.selectedColors():
                    self.working_sprite.remapColor(color, color_remap)

                self.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.working_sprite = copy(self.giveSprite()[0])

                color_remap = self.main_window.tool_widget.color_select_panel.getColorIndices()[
                    0]

                for color in self.main_window.tool_widget.color_select_panel.selectedColors():
                    self.working_sprite.changeBrightnessColor(1, color)

                self.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.FILL:

                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                # since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x()/self.zoom_factor)
                y = int(screen_pos.y()/self.zoom_factor)

                self.addSpriteToHistory()
                self.generateProtectionMask()

                self.fill(x, y, shade)
                return

        if event.button() == QtCore.Qt.RightButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:

                self.addSpriteToHistory()
                self.generateProtectionMask()
                self.working_sprite = copy(self.giveSprite()[0])

                color_remap = self.main_window.tool_widget.color_select_panel.getColorIndices()[
                    0]

                for color in self.main_window.tool_widget.color_select_panel.selectedColors():
                    self.working_sprite.changeBrightnessColor(-1, color)

                self.overdraw(x, y)
                return

    def viewMouseMoveEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        screen_pos = event.localPos()
        x = round(screen_pos.x()/self.zoom_factor)
        y = round(screen_pos.y()/self.zoom_factor)

        x_display = -int(self.canvas_size/2)+x
        y_display = -int(self.canvas_size*2/3)+y
        self.label_x.setText(f'X   {x_display}')
        self.label_y.setText(f'Y   {y_display}')

        # Control modifier = sprite control, dealt with by parent
        if modifiers == QtCore.Qt.ControlModifier:
            event.ignore()
            return

        if event.buttons() == QtCore.Qt.LeftButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:
                shade = self.main_window.giveActiveShade()
                if not shade:
                    return

                self.draw(x, y, shade)
                return

            if self.main_window.giveTool() == cwdg.Tools.ERASER:
                self.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.EYEDROPPER:

                # since the hotspot of the cross cursor is in the middle we have to round differently
                x = int(screen_pos.x()/self.zoom_factor)
                y = int(screen_pos.y()/self.zoom_factor)

                self.eyedrop(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.REMAP:
                if not self.working_sprite:
                    return

                self.overdraw(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:
                if not self.working_sprite:
                    return

                self.overdraw(x, y)
                return

        if event.buttons() == QtCore.Qt.RightButton:

            if self.main_window.giveTool() == cwdg.Tools.PEN:
                self.erase(x, y)
                return

            if self.main_window.giveTool() == cwdg.Tools.BRIGHTNESS:
                self.overdraw(x, y)
                return

        return

    def viewWheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.AltModifier:
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
                toolbox.dial_brushsize.setValue(
                    toolbox.dial_brushsize.value()+1)
            elif event.angleDelta().y() < 0:
                toolbox.dial_brushsize.setValue(
                    toolbox.dial_brushsize.value()-1)

    def updateView(self, skip_locked=False):
        if self.locked:
            if not skip_locked:
                self.object_tab.updateCurrentMainView()

                return

            canvas = self.object_tab.giveCurrentMainView(
                self.canvas_size, add_auxilaries=True)

        else:
            canvas = Image.new('RGBA', (self.canvas_size, self.canvas_size))

            # if add_auxiliaries and self.button_bounding_box.isChecked():
            #    backbox, coords_backbox = self.main_window.bounding_boxes.giveBackbox(self.o)
            #    canvas.paste(backbox, (int(canvas_size/2)+coords_backbox[0], int(canvas_size*2/3)+coords_backbox[1]), backbox)

            # canvas.paste(self.frame_image, self.frame_image)

            coords = (int(self.canvas_size/2)+self.sprite.x,
                      int(self.canvas_size*2/3)+self.sprite.y)

            canvas.paste(self.sprite.image, coords, self.sprite.image)

        canvas = canvas.resize((int(canvas.size[0]*self.zoom_factor), int(
            canvas.size[1]*self.zoom_factor)), resample=Image.NEAREST)
        image = ImageQt(canvas)

        pixmap = QtGui.QPixmap.fromImage(image)
        self.view.setPixmap(pixmap)

        geometry = self.scroll_area.geometry()
        scroll_width = max(self.view.size().width(), geometry.width())
        scroll_height = max(self.view.size().height(), geometry.height())

        self.scroll_area_content.resize(scroll_width, scroll_height)

    def giveSprite(self):
        if self.locked:
            return self.object_tab.giveCurrentMainViewSprite()
        else:
            return self.sprite, 0

    def addSpriteToHistory(self):
        sprite_import, index = self.giveSprite()
        sprite = copy(sprite_import)

        if len(self.history[index]) == self.main_window.settings['history_maximum']:
            self.history[index].pop(0)

        self.history[index].append(sprite)
        self.history_redo[index] = []

    def addSpriteToHistoryAllViews(self):
        if not self.locked:
            return

        for index, sprite_import in enumerate(self.object_tab.o.sprites.items()):
            sprite = copy(sprite_import[1])

            if len(self.history[index]) == self.main_window.settings['history_maximum']:
                self.history[index].pop(0)

            self.history[index].append(sprite)
            self.history_redo[index] = []

    def undo(self):
        sprite_old, index = self.giveSprite()

        if len(self.history[index]) == 0:
            return

        sprite_new = self.history[index].pop(-1)

        self.history_redo[index].append(copy(sprite_old))

        sprite_old.image = sprite_new.image
        sprite_old.x = sprite_new.x
        sprite_old.y = sprite_new.y

        self.updateView()

    def redo(self):
        sprite_old, index = self.giveSprite()

        if len(self.history_redo[index]) == 0:
            return

        sprite_new = self.history_redo[index].pop(-1)

        self.history[index].append(copy(sprite_old))

        sprite_old.image = sprite_new.image
        sprite_old.x = sprite_new.x
        sprite_old.y = sprite_new.y

        self.updateView()

    def paste(self):
        self.addSpriteToHistory()
        if self.locked:
            self.object_tab.sprites_tab.pasteSpriteFromClipboard()
        else:
            pass

    def copy(self):
        if self.locked:
            self.object_tab.sprites_tab.copySpriteToClipboard()
        else:
            pass


class SpriteViewWidget(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tab = None

        self.slider_zoom = None
        self.current_pressed_key = None
        self.mousepos = QtCore.QPoint(0, 0)

        self.setVerticalScrollBar(
            self.KeepPositionScrollBar(QtCore.Qt.Vertical, self))
        self.setHorizontalScrollBar(
            self.KeepPositionScrollBar(QtCore.Qt.Horizontal, self))

    def connectTab(self, tab):
        self.tab = tab
        self.slider_zoom = tab.slider_zoom

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        # we ignore the event when Alt is pressed as it is the color change movement
        if modifiers in (QtCore.Qt.ShiftModifier, QtCore.Qt.AltModifier):
            return

        if not self.slider_zoom:
            super().wheelEvent()
            return

        if modifiers == QtCore.Qt.ControlModifier:
            zoom_factor = self.slider_zoom.value()
            if event.angleDelta().y() > 0 and zoom_factor != self.slider_zoom.maximum():
                self.slider_zoom.setValue(int(zoom_factor+1))
            elif event.angleDelta().y() < 0 and zoom_factor != self.slider_zoom.minimum():
                self.slider_zoom.setValue(int(zoom_factor-1))
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if event.button() == QtCore.Qt.LeftButton and modifiers == QtCore.Qt.ControlModifier:
            QApplication.setOverrideCursor(QtCore.Qt.ClosedHandCursor)
            self.mousepos = event.localPos()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        delta = event.localPos() - self.mousepos

        # panning area
        if event.buttons() == QtCore.Qt.LeftButton and modifiers == QtCore.Qt.ControlModifier:
            h = self.horizontalScrollBar().value()
            v = self.verticalScrollBar().value()

            self.horizontalScrollBar().setValue(int(h - delta.x()))
            self.verticalScrollBar().setValue(int(v - delta.y()))

        self.mousepos = event.localPos()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        self.mousepos = event.localPos()
        super().mouseReleaseEvent(event)

    class KeepPositionScrollBar(QScrollBar):
        defaultRatio = .5
        ratio = .5

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.rangeChanged.connect(self.restoreRatio)
            self.valueChanged.connect(self.updateRatio)

        def restoreRatio(self):
            absValue = (self.maximum() - self.minimum()) * self.ratio
            self.setValue(round(self.minimum() + absValue))

        def updateRatio(self):
            if self.maximum() - self.minimum():
                absValue = self.value() - self.minimum()
                self.ratio = absValue / (self.maximum() - self.minimum())
            else:
                self.ratio = self.defaultRatio


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
            self.main_window.current_palette, True, True, True)

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

        self.button_remap_to.clicked.connect(self.colorRemapTo)
        self.button_incr_brightness.clicked.connect(
            lambda x, step=1: self.colorChangeBrightness(step))
        self.button_decr_brightness.clicked.connect(
            lambda x, step=-1: self.colorChangeBrightness(step))
        self.button_remove_color.clicked.connect(self.colorRemove)

    # Color manipulations

    def colorRemapTo(self):
        color_remap = self.combobox_remap_to_color.currentText()
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()

            widget.colorRemapToAll(color_remap, selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()

            widget.colorRemap(color_remap, selected_colors)

    def colorChangeBrightness(self, step):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()

            widget.colorChangeBrightnessAll(step, selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()

            widget.colorChangeBrightness(step, selected_colors)

    def colorRemove(self):
        selected_colors = self.color_select_panel.selectedColors()

        if self.checkbox_all_views.isChecked():
            widget = self.main_window.object_tabs.currentWidget()

            widget.colorRemoveAll(selected_colors)

        else:
            widget = self.main_window.sprite_tabs.currentWidget()

            widget.colorRemove(selected_colors)


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

    def loadSSSettings(self, settings):
        for flag in cts.Jsmall_flags:
            checkbox = self.tab_SS_default.findChild(QCheckBox, flag)
            if checkbox:
                checkbox.setChecked(settings.get(
                    'small_scenery_defaults', {}).get(flag, False))

        checkbox = self.tab_SS_default.findChild(QCheckBox, 'isTree')
        checkbox.setChecked(settings.get(
            'small_scenery_defaults', {}).get('isTree', False))

        self.cursor_box = self.tab_SS_default.findChild(
            QComboBox, "comboBox_cursor")

        for cursor in cts.cursors:
            self.cursor_box.addItem(cursor.replace('_', ' '))

        self.cursor_box.setCurrentText(settings.get(
            'small_scenery_defaults', {}).get('cursor', 'CURSOR BLANK'))

        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_price")
        spinbox.setValue(
            int(settings.get('small_scenery_defaults', {}).get('price', 1)))
        spinbox = self.tab_SS_default.findChild(
            QSpinBox, "spinBox_removalPrice")
        spinbox.setValue(
            int(settings.get('small_scenery_defaults', {}).get('removalPrice', 1)))

    def clickChangeFolder(self, sender):

        directory = sender.text() if sender.text() != '' else "%USERPROFILE%/Documents/"
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", directory=directory)
        if folder:
            sender.setText(folder)

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

        ss_defaults = {}
        for flag in cts.Jsmall_flags:
            checkbox = self.tab_SS_default.findChild(QCheckBox, flag)
            if checkbox:
                ss_defaults[flag] = checkbox.isChecked()

        ss_defaults['isTree'] = self.isTree.isChecked()

        spinbox = self.tab_SS_default.findChild(QSpinBox, "spinBox_price")
        ss_defaults['price'] = spinbox.value()
        spinbox = self.tab_SS_default.findChild(
            QSpinBox, "spinBox_removalPrice")
        ss_defaults['removalPrice'] = spinbox.value()

        ss_defaults['cursor'] = self.tab_SS_default.findChild(
            QComboBox, "comboBox_cursor").currentText().replace(' ', '_')

        settings['small_scenery_defaults'] = ss_defaults

        return settings

    def accept(self):

        self.ret = self.retrieveInputs()
        super().accept()
