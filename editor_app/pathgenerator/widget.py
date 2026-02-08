# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""


from PyQt5.QtWidgets import QMainWindow, QDialog, QMenu, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QApplication, QWidget, QTabWidget, QToolButton, QComboBox, QScrollArea, \
    QScrollBar, QPushButton, QLineEdit, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QListWidget, QListWidgetItem, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5 import uic, QtGui, QtCore
from PIL import Image, ImageEnhance
from PIL.ImageQt import ImageQt
from customwidgets import ColorSelectWidget
import sys
import io
from os import getcwd
import re

import pathgenerator.generator as gen
import auxiliaries as aux

from rctobject import palette as pal
from rctobject import sprites as spr

# om.rotate(-45, Image.NEAREST).resize((64,31),Image.NEAREST)

class PathGeneratorTab(QWidget):
    mainViewUpdated = QtCore.pyqtSignal()
    rotationChanged = QtCore.pyqtSignal(int)
    boundingBoxChanged = QtCore.pyqtSignal(
        [bool, object, tuple], [bool, object, tuple, tuple])
    symmAxesChanged = QtCore.pyqtSignal(bool, object, tuple)
    activeLayerRowChanged = QtCore.pyqtSignal(int)
    
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window
        self.generator = gen.PathGenerator(self.loadFixMask(), main_window)
        self.loadFrame()
        
        self.locked = False
        self.locked_sprite_tab = False

        layout = QHBoxLayout()

        self.sprites_tab = SpritesTab(self, main_window)
        self.settings_tab = SettingsTab(self, main_window, self.sprites_tab)
        

        layout.addWidget(self.sprites_tab)
        layout.addWidget(self.settings_tab)

        self.setLayout(layout)
        
    def isObject(self):
        return False
    
    def giveDummy(self):
        return self.settings_tab.giveDummy()

    def lockWithSpriteTab(self, locked_sprite_tab):
        if self.locked:
            self.unlockSpriteTab()

        self.locked = True        
        self.locked_sprite_tab = locked_sprite_tab
        self.locked_sprite_tab.layerUpdated.connect(
            lambda: self.updateCurrentMainView(emit_signal=False))
        
        self.sprites_tab.createLayers()


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




class SettingsTab(QWidget):
    def __init__(self, generator_tab: PathGeneratorTab, sprites_tab: QWidget):
        super().__init__()
        uic.loadUi(aux.resource_path("pathgenerator/gui/settingsPTG.ui"), self)

        self.generator_tab = generator_tab
        self.sprites_tab = sprites_tab
        self.main_window = generator_tab.main_window
        
        self.button_change_output_folder = self.findChild(
            QPushButton, "pushButton_changeOutputFolder")
        self.button_generate = self.findChild(
            QPushButton, "pushButton_generate")
        self.button_select_all_templates = self.findChild(
            QPushButton, "pushButton_selectAllTemplates")
        self.button_clear_all_templates = self.findChild(
            QPushButton, "pushButton_clearAllTemplates")
        self.button_import_template = self.findChild(
            QPushButton, "pushButton_importTemplate")

        self.checkbox_auto_naming = self.findChild(
            QCheckBox, "checkBox_autoNaming")
        self.checkbox_raised = self.findChild(
            QCheckBox, "checkBox_raised")

        self.combobox_rotation = self.findChild(
            QComboBox, "comboBox_rotation")

        self.label_display_name = self.findChild(QLabel, "label_displayName")
        self.label_prefix = self.findChild(QLabel, "label_prefix")
        self.label_suffix = self.findChild(QLabel, "label_suffix")
        self.label_generate_return = self.findChild(
            QLabel, "label_GenerateReturn")

        self.combobox_remap_to_color = self.findChild(
            QComboBox, "comboBox_remapToColor")

        self.lineedit_author = self.findChild(QLineEdit, "lineEdit_author")
        self.lineedit_author_id = self.findChild(QLineEdit, "lineEdit_authorID")
        self.lineedit_object_id = self.findChild(QLineEdit, "lineEdit_objectID")
        self.lineedit_prefix = self.findChild(QLineEdit, "lineEdit_prefix")
        self.lineedit_suffix = self.findChild(QLineEdit, "lineEdit_suffix")
        self.lineedit_output_folder = self.findChild(
            QLineEdit, "lineEdit_outputFolder")
     
        self.listwidget_template_list = self.findChild(
            QListWidget, "listWidget_templateList")

        # Set defaults
        self.setDefaults()
        self.loadTemplates()

        # Add functions
        self.button_select_all_templates.clicked.connect(
            self.listwidget_template_list.selectAll)
        self.button_clear_all_templates.clicked.connect(
            self.listwidget_template_list.clearSelection)
        self.button_import_template.clicked.connect(self.clickImportTemplate)
        self.button_change_output_folder.clicked.connect(
            self.clickChangeOutputFolder)
        self.button_generate.clicked.connect(self.clickGenerate)

        self.checkbox_auto_naming.stateChanged.connect(self.clickBoxAutoNaming)
        self.combobox_rotation.currentIndexChanged.connect(self.rotationChanged)

        self.lineedit_prefix.textChanged.connect(self.updateDisplayName)
        self.lineedit_suffix.textChanged.connect(self.updateDisplayName)

    def setDefaults(self):
        settings = self.main_window.settings

        self.lineedit_author.setText(settings.get('author', ''))
        self.lineedit_author_id.setText(settings.get('author_id', ''))
        
        self.lineedit_suffix.hide()
        self.label_suffix.hide()
        self.label_prefix.setText('')

        self.lineedit_output_folder.setText(settings.get('savedefault', ''))

    def clickChangeOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory")
        if folder:
            self.lineedit_output_folder.setText(folder)

    def clickBoxAutoNaming(self, state):
        self.generator.settings['autoNaming'] = (state == QtCore.Qt.Checked)
        if state == QtCore.Qt.Checked:
            self.lineedit_suffix.show()
            self.label_suffix.show()
            self.label_prefix.setText('Prefix')
        else:
            self.lineedit_suffix.hide()
            self.lineedit_suffix.setText('')
            self.label_suffix.hide()
            self.label_prefix.setText('')
            
        self.updateDisplayName()

    def clickGenerate(self):
        self.label_generate_return.setText('')

        self.generator.setName(self.lineedit_prefix.text(),
                               self.lineedit_suffix.text())
        self.generator.settings['author'] = re.split('\,\s*', self.lineedit_author.text())
        self.generator.settings['author_id'] = self.lineedit_author_id.text()
        self.generator.settings['object_id'] = self.lineedit_object_id.text()
        self.generator.settings['raised'] = self.checkbox_raised.isChecked()
        self.generator.selected_templates = [
            sel.text() for sel in self.listwidget_template_list.selectedItems()]

        return_text = self.generator.generate(self.lineedit_output_folder.text())

        self.label_generate_return.setText(return_text)
        self.updateMainView()

    def rotationChanged(self, item):
        self.previewClicked(0)
        self.generator.rotationOptionChanged(item)

        if item == 0:

            self.sprites_tab.button_auto_rotate1.setEnabled(False)
            self.sprites_tab.button_auto_rotate2.setEnabled(False)

            for widget in self.sprites_tab.sprite_preview:
                widget.hide()

        else:

            self.sprites_tab.button_auto_rotate1.setEnabled(True)
            self.sprites_tab.button_auto_rotate2.setEnabled(True)

            for widget in self.sprites_tab.sprite_preview:
                widget.show()

        self.updateMainView()
        self.updatePreview(0)
        self.updatePreview(1)
        self.updatePreview(2)
        self.updatePreview(3)

    def clickGenerateRotations(self, direction):
        self.generator.fixBaseToMask()
        self.generator.generateRotations(direction)

        self.updateMainView()
        self.updatePreview(0)
        self.updatePreview(1)
        self.updatePreview(2)
        self.updatePreview(3)

    def clickImportTemplate(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Template File", "", "Template File (*.template)")

        if filepath:
            name = self.generator.loadTemplate(filepath)

            if name:
                self.listwidget_template_list.addItem(name)
            else:
                pass

    def resetAllBases(self):
        self.generator.resetAllBases()

        self.updatePreview(0)
        self.updatePreview(1)
        self.updatePreview(2)
        self.updatePreview(3)
        self.previewClicked(0)

    # Auxiliary functions

    def updateMainView(self):
        canvas = Image.new('RGBA', (172, 132))
        canvas.paste(
            self.generator.base.show(), (86+self.generator.base.x, 50+self.generator.base.y), self.generator.base.image)
        canvas.paste(self.frame_image, self.frame_image)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.spriteViewLabel.setPixmap(pixmap)

        self.updatePreview(self.generator.current_rotation)

    def updatePreview(self, rot):

        im = self.generator.bases[rot].show()

        coords = (0, 2)

        canvas = Image.new('RGBA', (68, 34))
        canvas.paste(im, coords, im)
        # canvas.paste(self.frame_image, self.frame_image)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.sprite_preview[rot].setPixmap(pixmap)

    def updateDisplayName(self):
        if self.generator.settings['autoNaming']:
            self.label_display_name.setText(
                self.lineedit_prefix.text() + ' Fulltile ' + self.lineedit_suffix.text())
        else:
            self.label_display_name.setText(self.lineedit_prefix.text())

    def loadFrame(self):
        img = QtGui.QImage(aux.resource_path("pathgenerator/res/frame.png"))
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        self.frame_image = Image.open(io.BytesIO(buffer.data()))
        buffer.close()

    def loadFixMask(self):
        img = QtGui.QImage(aux.resource_path("pathgenerator/res/fix_mask.png"))
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        image = Image.open(io.BytesIO(buffer.data()))
        buffer.close()

        return image

    def loadTemplates(self):
        for name in self.generator.templates.keys():
            self.listwidget_template_list.addItem(name)

    # Events

    def mousePressEvent(self, e):
        self.label_generate_return.setText("")
        
class SpritesTab(QWidget):
    def __init__(self, generator_tab: PathGeneratorTab):
        super().__init__()
        
        self.generator_tab = generator_tab
        self.main_window = generator_tab.main_window
        
    def initializeWidgets(self, view_width, view_height):
        # Buttons load/reset
        self.button_load_base = self.findChild(
            QPushButton, "pushButton_loadImageButton")
        self.button_import_texture = self.findChild(
            QPushButton, "pushButton_importTexture")
        self.button_fix_to_mask = self.findChild(
            QPushButton, "pushButton_fixToMask")


        self.button_load_base.clicked.connect(self.loadBase)
        self.button_import_texture.clicked.connect(self.importBase)
        self.button_fix_to_mask.clicked.connect(self.fixToMask)

        self.button_cycle_rotation = self.findChild(
            QPushButton, "pushButton_cycleRotation")

        self.button_cycle_rotation.clicked.connect(self.cycleRotation)
        
        self.button_auto_rotate1 = self.findChild(
            QPushButton, "pushButton_autoRotate1")
        self.button_auto_rotate2 = self.findChild(
            QPushButton, "pushButton_autoRotate2")
        
        self.button_auto_rotate1.clicked.connect(
            lambda x: self.clickGenerateRotations(0))
        self.button_auto_rotate2.clicked.connect(
            lambda x: self.clickGenerateRotations(1))

        # View main
        self.sprite_view_main.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sprite_view_main.customContextMenuRequested.connect(
            self.showSpriteMenu)
        self.sprite_view_main.setBackgroundBrush(
            QtGui.QBrush(
                QtGui.QColor(
                    self.main_window.current_background_color[0],
                    self.main_window.current_background_color[1],
                    self.main_window.current_background_color[2])))

        self.sprite_view_main_item = QGraphicsPixmapItem()
        self.sprite_view_main_scene = QGraphicsScene()
        self.sprite_view_main_scene.addItem(self.sprite_view_main_item)
        self.sprite_view_main_scene.setSceneRect(0, 0, view_width, view_height)
        self.sprite_view_main.setScene(self.sprite_view_main_scene)

        # Previews
        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1,
                               self.sprite_view_preview2, self.sprite_view_preview3]
        for rot, widget in enumerate(self.sprite_preview):
            self.sprite_preview[rot].mousePressEvent = (
                lambda e, rot=rot: self.previewClicked(rot))
            self.sprite_preview[rot].setStyleSheet(
                f"background-color :  rgb{self.main_window.current_background_color};")

        # Remap Color Buttons
        self.button_first_remap = self.findChild(
            QPushButton, 'pushButton_firstRemap')
        self.button_first_remap.colorChanged.connect(
            lambda color, remap="1st Remap": self.clickChangeRemap(color, remap=remap))
        self.button_first_remap.setColor(self.main_window.settings.get(
            'default_remaps', ['NoColor', 'NoColor', 'NoColor'])[0])

        self.button_second_remap = self.findChild(
            QPushButton, 'pushButton_secondRemap')
        self.button_second_remap.colorChanged.connect(
            lambda color, remap="2nd Remap": self.clickChangeRemap(color, remap=remap))
        self.button_second_remap.setColor(self.main_window.settings.get(
            'default_remaps', ['NoColor', 'NoColor', 'NoColor'])[1])

        self.button_third_remap = self.findChild(
            QPushButton, 'pushButton_thirdRemap')
        self.button_third_remap.colorChanged.connect(
            lambda color, remap="3rd Remap": self.clickChangeRemap(color, remap=remap))
        self.button_third_remap.setColor(self.main_window.settings.get(
            'default_remaps', ['NoColor', 'NoColor', 'NoColor'])[2])

        self.button_first_remap.panelOpened.connect(
            self.button_second_remap.hidePanel)
        self.button_first_remap.panelOpened.connect(
            self.button_third_remap.hidePanel)

        self.button_second_remap.panelOpened.connect(
            self.button_first_remap.hidePanel)
        self.button_second_remap.panelOpened.connect(
            self.button_third_remap.hidePanel)

        self.button_third_remap.panelOpened.connect(
            self.button_second_remap.hidePanel)
        self.button_third_remap.panelOpened.connect(
            self.button_first_remap.hidePanel)
        
    def loadBase(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Base Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            self.generator.loadBase(filepath)

        self.updateMainView()

    def importBase(self):
        dialog = ImportSpriteUi()

        if dialog.exec():
            ret = dialog.ret
            if isinstance(ret, Image.Image):
                self.generator.importBases([ret])
                self.comboboxRotation.setCurrentIndex(0)
            elif isinstance(ret, list):
                self.generator.importBases(ret)
                self.comboboxRotation.setCurrentIndex(1)
            self.previewClicked(0)

            self.updatePreview(1)
            self.updatePreview(2)
            self.updatePreview(3)

    def fixToMask(self):
        self.generator.fixBaseToMask()
        self.updateMainView()


class ImportSpriteUi(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(aux.resource_path("pathgenerator/gui/importsprite.ui"), self)
        self.setWindowIcon(QtGui.QIcon(aux.resource_path("gui/icon.png")))

        self.setFixedSize(self.size())

        self.loadFixMask()
        self.loadFrame()
        self.x = 0
        self.y = 0
        self.base = Image.new('RGBA', (1, 1))

        self.contrast = 1.0
        self.sharpness = 1.0
        self.brightness = 1.0

        self.factor = 1
        self.angle = 0

        self.spriteViewLabel = self.findChild(QLabel, "sprite_view")
        self.spritePreviewLabel = self.findChild(QLabel, "sprite_preview")

        self.buttonLoadBase = self.findChild(
            QPushButton, "pushButton_loadImageButton")
        self.buttonLoadBase.clicked.connect(self.clickLoadImage)

        self.boxAngle = self.findChild(QSpinBox, "spinBox_angle")
        self.boxAngle.valueChanged.connect(self.angleChanged)

        self.sliderZoom = self.findChild(QSlider, "slider_zoom")
        self.sliderZoom.valueChanged.connect(self.zoomChanged)

        self.sliderContrast = self.findChild(QSlider, "slider_contrast")
        self.sliderContrast.valueChanged.connect(self.contrastChanged)

        self.sliderBrightness = self.findChild(QSlider, "slider_brightness")
        self.sliderBrightness.valueChanged.connect(self.brightnessChanged)

        self.sliderSharpness = self.findChild(QSlider, "slider_sharpness")
        self.sliderSharpness.valueChanged.connect(self.sharpnessChanged)

        # Sprite control buttons
        self.buttonSpriteLeft = self.findChild(
            QToolButton, "toolButton_left")
        self.buttonSpriteDown = self.findChild(
            QToolButton, "toolButton_down")
        self.buttonSpriteRight = self.findChild(
            QToolButton, "toolButton_right")
        self.buttonSpriteUp = self.findChild(
            QToolButton, "toolButton_up")
        self.buttonSpriteLeftRight = self.findChild(
            QToolButton, "toolButton_leftright")
        self.buttonSpriteUpDown = self.findChild(
            QToolButton, "toolButton_updown")

        self.buttonSpriteLeft.clicked.connect(
            lambda x: self.clickSpriteControl('left'))
        self.buttonSpriteDown.clicked.connect(
            lambda x: self.clickSpriteControl('down'))
        self.buttonSpriteRight.clicked.connect(
            lambda x: self.clickSpriteControl('right'))
        self.buttonSpriteUp.clicked.connect(
            lambda x: self.clickSpriteControl('up'))
        self.buttonSpriteLeftRight.clicked.connect(
            lambda x: self.clickSpriteControl('leftright'))
        self.buttonSpriteUpDown.clicked.connect(
            lambda x: self.clickSpriteControl('updown'))

    def clickSpriteControl(self, direction: str):
        if direction == 'left':
            self.x -= 1
        elif direction == 'right':
            self.x += 1
        elif direction == 'up':
            self.y -= 1
        elif direction == 'down':
            self.y += 1
        elif direction == 'leftright':
            self.base = self.base.transpose(
                Image.FLIP_LEFT_RIGHT)
        elif direction == 'updown':
            self.base = self.base.transpose(
                Image.FLIP_TOP_BOTTOM)

        self.updateMainView()

    def loadFrame(self):
        img = QtGui.QImage(aux.resource_path("pathgenerator/res/frame_import.png"))
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        self.frame_image = Image.open(io.BytesIO(buffer.data()))
        buffer.close()

    def loadFixMask(self):
        img = QtGui.QImage(aux.resource_path("pathgenerator/res/import_mask.png"))
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        self.fix_mask = Image.open(io.BytesIO(buffer.data()))
        buffer.close()

    def clickBoxAllRotations(self, state, color):
        self.rotations_included = (
            state == QtCore.Qt.Checked)

    def clickLoadImage(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Base Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            self.base = Image.open(filepath).convert('RGBA')
            self.base.crop(self.base.getbbox())
            self.sliderContrast.setValue(100)
            self.sliderBrightness.setValue(100)
            self.sliderSharpness.setValue(100)

        self.updateMainView()

    def angleChanged(self, val):
        self.angle = val

        self.updateMainView()

    def zoomChanged(self, val):
        if val > 0:
            self.factor = 1.5**(val/10)
        else:
            self.factor = 2**(val/10)

        self.updateMainView()

    def contrastChanged(self, val):
        self.contrast = val/100

        self.updateMainView()

    def brightnessChanged(self, val):
        self.brightness = val/100

        self.updateMainView()

    def sharpnessChanged(self, val):
        self.sharpness = val/100

        self.updateMainView()

    def updateMainView(self):
        base = self.base.resize(
            (int(self.base.size[0] * self.factor),
             int(self.base.size[1] * self.factor)),
            resample=Image.BICUBIC).rotate(
            self.angle, resample=Image.BICUBIC, expand=1)

        x = self.x - int(base.size[0]/2)
        y = self.y - int(base.size[1]/2)

        canvas = Image.new('RGBA', (172, 132))
        canvas.paste(
            base, (88+x, 66+y), base)
        canvas.paste(self.frame_image, self.frame_image)

        image = ImageQt(canvas)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.spriteViewLabel.setPixmap(pixmap)

        self.updatePreview(base)

    def updatePreview(self, base):
        if self.base.size == (1, 1):
            return

        else:

            x = self.x - int(base.size[0]/2)
            y = self.y - int(base.size[1]/2)

            im = self.fixToMask(base, x, y)

            if self.contrast != 1:
                im = ImageEnhance.Contrast(im).enhance(self.contrast)
            if self.brightness != 1:
                im = ImageEnhance.Brightness(im).enhance(self.brightness)
            if self.sharpness != 1:
                im = ImageEnhance.Sharpness(im).enhance(self.sharpness)

            canvas = Image.new('RGBA', (71, 71))
            canvas.paste(
                im, (3, 21), im)

            image = ImageQt(canvas)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.spritePreviewLabel.setPixmap(pixmap)

    def accept(self):

        if self.base.size == (1, 1):
            super().reject()
        else:
            base = self.base.resize(
                (int(self.base.size[0] * self.factor),
                 int(self.base.size[1] * self.factor)),
                resample=Image.BICUBIC).rotate(
                self.angle, resample=Image.BICUBIC, expand=1)

            x = self.x - int(base.size[0]/2)
            y = self.y - int(base.size[1]/2)

            if self.checkBox_rotations.isChecked():
                self.ret = []
                for rot in range(4):
                    im = self.fixToMask(base, x, y, rot)

                    if self.contrast != 1:
                        im = ImageEnhance.Contrast(im).enhance(self.contrast)
                    if self.brightness != 1:
                        im = ImageEnhance.Brightness(
                            im).enhance(self.brightness)
                    if self.sharpness != 1:
                        im = ImageEnhance.Sharpness(im).enhance(self.sharpness)

                    self.ret.append(im)

            else:
                im = self.fixToMask(base, x, y)

                if self.contrast != 1:
                    im = ImageEnhance.Contrast(im).enhance(self.contrast)
                if self.brightness != 1:
                    im = ImageEnhance.Brightness(im).enhance(self.brightness)
                if self.sharpness != 1:
                    im = ImageEnhance.Sharpness(im).enhance(self.sharpness)

                self.ret = im

            super().accept()

    def fixToMask(self, image, x, y, rot=0):
        mask = self.fix_mask.copy()
        image = image.crop(
            (-23-x, -23-y, -x+23, -y+23))
        image = image.rotate(rot*90, Image.BICUBIC)
        mask.paste(image, mask)

        return mask.rotate(-45, Image.NEAREST, expand=1).crop((1, 2, 65, 64)).resize((64, 31), Image.NEAREST)
