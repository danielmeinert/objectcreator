# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QWidget, QGroupBox, QToolButton, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QSlider, QSpinBox, QDoubleSpinBox, QListWidget, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PIL import Image, ImageEnhance
from PIL.ImageQt import ImageQt
from customwidgets import ColorSelectWidget
import sys
import io
from os import getcwd

import pathgenerator.generator as gen
import auxiliaries as aux

from rctobject import palette as pal
from rctobject import sprites as spr

# om.rotate(-45, Image.NEAREST).resize((64,31),Image.NEAREST)


class PathGeneratorWidget(QWidget):
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        uic.loadUi(aux.resource_path("pathgenerator/gui/pathtile_generator.ui"), self)
        self.setWindowIcon(QtGui.QIcon(aux.resource_path("gui/icon.png")))

        self.main_window = main_window
        self.generator = gen.PathGenerator(self.loadFixMask(), main_window)
        self.loadFrame()

        # Define Widgets
        self.spriteViewLabel = self.findChild(QLabel, "sprite_view")

        self.buttonLoadBase = self.findChild(
            QPushButton, "pushButton_loadImageButton")
        self.buttonImportTexture = self.findChild(
            QPushButton, "pushButton_importTexture")
        self.buttonFixToMask = self.findChild(
            QPushButton, "pushButton_fixToMask")

        self.buttonChangeOutputFolder = self.findChild(
            QPushButton, "pushButton_changeOutputFolder")
        self.buttonGenerate = self.findChild(
            QPushButton, "pushButton_generate")
        self.buttonSelectAllTemplates = self.findChild(
            QPushButton, "pushButton_selectAllTemplates")
        self.buttonClearAllTemplates = self.findChild(
            QPushButton, "pushButton_clearAllTemplates")

        self.buttonRemapTo = self.findChild(
            QPushButton, "pushButton_remapTo")
        self.buttonIncrBrightness = self.findChild(
            QPushButton, "pushButton_incrBrightness")
        self.buttonDecrBrightness = self.findChild(
            QPushButton, "pushButton_decrBrightness")
        self.buttonImportTemplate = self.findChild(
            QPushButton, "pushButton_importTemplate")

        self.checkboxAllViews = self.findChild(
            QCheckBox, "checkBox_allViews")
        self.checkboxAutoNaming = self.findChild(
            QCheckBox, "checkBox_autoNaming")
        self.checkbox_raised = self.findChild(
            QCheckBox, "checkBox_raised")

        self.comboboxRotation = self.findChild(
            QComboBox, "comboBox_rotation")
        self.buttonAutoRotate1 = self.findChild(
            QPushButton, "pushButton_autoRotate1")
        self.buttonAutoRotate2 = self.findChild(
            QPushButton, "pushButton_autoRotate2")

        self.labelDisplayName = self.findChild(QLabel, "label_displayName")
        self.labelPrefix = self.findChild(QLabel, "label_prefix")
        self.labelSuffix = self.findChild(QLabel, "label_suffix")
        self.labelGenerateReturn = self.findChild(
            QLabel, "label_GenerateReturn")

        self.comboboxRemapToColor = self.findChild(
            QComboBox, "comboBox_remapToColor")

        self.lineeditAuthor = self.findChild(QLineEdit, "lineEdit_author")
        self.lineeditAuthorID = self.findChild(QLineEdit, "lineEdit_authorID")
        self.lineeditObjectID = self.findChild(QLineEdit, "lineEdit_objectID")
        self.lineeditPrefix = self.findChild(QLineEdit, "lineEdit_prefix")
        self.lineeditSuffix = self.findChild(QLineEdit, "lineEdit_suffix")
        self.lineeditOutputFolder = self.findChild(
            QLineEdit, "lineEdit_outputFolder")

        # Color Panel
        self.widgetColorPanel = self.findChild(
            QGroupBox, "groupBox_selectedColor")
        self.colorSelectPanel = ColorSelectWidget(pal.orct)
        self.widgetColorPanel.layout().addWidget(self.colorSelectPanel)

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

        # Rotation buttons
        self.sprite_preview = [self.sprite_view_preview0, self.sprite_view_preview1,
                               self.sprite_view_preview2, self.sprite_view_preview3]

        for rot, widget in enumerate(self.sprite_preview):
            widget.mousePressEvent = (
                lambda e, rot=rot: self.previewClicked(rot))
            widget.hide()

            self.updatePreview(rot)

        self.previewClicked(0)

        self.listwidgetTemplateList = self.findChild(
            QListWidget, "listWidget_templateList")

        # Set defaults
        self.lineeditAuthor.setText(self.generator.settings['author'])
        self.lineeditAuthorID.setText(self.generator.settings['author_id'])
        self.lineeditSuffix.hide()
        self.labelSuffix.hide()
        self.labelPrefix.setText('')

        self.lineeditOutputFolder.setText(f'{getcwd()}\\output')

        self.comboboxRemapToColor.addItems(
            list(self.generator.current_palette.color_dict))
        self.comboboxRemapToColor.setCurrentIndex(
            self.generator.current_palette.color_dict['1st Remap'])

        self.loadTemplates()

        # Add functions
        self.buttonLoadBase.clicked.connect(self.clickLoadBase)
        self.buttonImportTexture.clicked.connect(self.importBase)
        self.buttonFixToMask.clicked.connect(self.clickFixToMask)
        self.buttonSelectAllTemplates.clicked.connect(
            self.listwidgetTemplateList.selectAll)
        self.buttonClearAllTemplates.clicked.connect(
            self.listwidgetTemplateList.clearSelection)
        self.buttonImportTemplate.clicked.connect(self.clickImportTemplate)
        self.buttonChangeOutputFolder.clicked.connect(
            self.clickChangeOutputFolder)
        self.buttonGenerate.clicked.connect(self.clickGenerate)

        self.buttonRemapTo.clicked.connect(self.clickRemapTo)
        self.buttonIncrBrightness.clicked.connect(self.clickIncrBrightness)
        self.buttonDecrBrightness.clicked.connect(self.clickDecrBrightness)

        self.checkboxAutoNaming.stateChanged.connect(self.clickBoxAutoNaming)
        self.comboboxRotation.currentIndexChanged.connect(self.rotationChanged)

        self.lineeditPrefix.textChanged.connect(self.updateDisplayName)
        self.lineeditSuffix.textChanged.connect(self.updateDisplayName)

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

        self.buttonSpriteLeft.setAutoRepeat(True)
        self.buttonSpriteDown.setAutoRepeat(True)
        self.buttonSpriteRight.setAutoRepeat(True)
        self.buttonSpriteUp.setAutoRepeat(True)

        self.buttonAutoRotate1.clicked.connect(
            lambda x: self.clickGenerateRotations(0))
        self.buttonAutoRotate2.clicked.connect(
            lambda x: self.clickGenerateRotations(1))


        self.show()

    # Event functions
    def clickLoadBase(self):

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Base Image", "", "PNG Images (*.png);; BMP Images (*.bmp)")

        if filepath:
            self.generator.loadBase(filepath)

        self.updateMainView()

    def clickFixToMask(self):

        self.generator.fixBaseToMask()
        self.updateMainView()

    # def clickResetBase(self):

    #    self.generator.base.resetSprite()
    #    self.updateMainView()

    def clickChangeOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory")
        if folder:
            self.lineeditOutputFolder.setText(folder)

    def clickBoxColorPanel(self, state, color):
        self.generator.selected_colors[color] = (
            state == QtCore.Qt.Checked)

    def clickBoxAutoNaming(self, state):
        self.generator.settings['autoNaming'] = (state == QtCore.Qt.Checked)
        if state == QtCore.Qt.Checked:
            self.lineeditSuffix.show()
            self.labelSuffix.show()
            self.labelPrefix.setText('Prefix')
        else:
            self.lineeditSuffix.hide()
            self.lineeditSuffix.setText('')
            self.labelSuffix.hide()
            self.labelPrefix.setText('')
        self.updateDisplayName()

    def clickGenerate(self):
        self.labelGenerateReturn.setText('')

        self.generator.setName(self.lineeditPrefix.text(),
                               self.lineeditSuffix.text())
        self.generator.settings['author'] = [
            auth.strip() for auth in self.lineeditAuthor.text().split(',')]
        self.generator.settings['author_id'] = self.lineeditAuthorID.text()
        self.generator.settings['object_id'] = self.lineeditObjectID.text()
        self.generator.settings['raised'] = self.checkbox_raised.isChecked()
        self.generator.selected_templates = [
            sel.text() for sel in self.listwidgetTemplateList.selectedItems()]

        return_text = self.generator.generate(self.lineeditOutputFolder.text())

        self.labelGenerateReturn.setText(return_text)
        self.updateMainView()

    def rotationChanged(self, item):
        self.previewClicked(0)
        self.generator.rotationOptionChanged(item)

        if item == 0:

            self.buttonAutoRotate1.setEnabled(False)
            self.buttonAutoRotate2.setEnabled(False)
            self.checkboxAllViews.setEnabled(False)

            for widget in self.sprite_preview:
                widget.hide()

        else:

            self.buttonAutoRotate1.setEnabled(True)
            self.buttonAutoRotate2.setEnabled(True)
            self.checkboxAllViews.setEnabled(True)
            for widget in self.sprite_preview:
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
                self.listwidgetTemplateList.addItem(name)
            else:
                pass

    def clickRemapTo(self):
        color_remap = self.comboboxRemapToColor.currentText()

        if self.checkboxAllViews.isChecked():
            for base in self.generator.bases:
                for color in self.colorSelectPanel.selectedColors():
                    base.remapColor(color, color_remap)

            self.updatePreview(0)
            self.updatePreview(1)
            self.updatePreview(2)
            self.updatePreview(3)

        else:
            for color in self.colorSelectPanel.selectedColors():
                self.generator.base.remapColor(color, color_remap)

        self.updateMainView()

    def clickIncrBrightness(self):
        if self.checkboxAllViews.isChecked():
            for base in self.generator.bases:
                for color in self.colorSelectPanel.selectedColors():
                    base.changeBrightnessColor(1, color)

            self.updatePreview(0)
            self.updatePreview(1)
            self.updatePreview(2)
            self.updatePreview(3)

        else:
            for color in self.colorSelectPanel.selectedColors():
                self.generator.base.changeBrightnessColor(1, color)

        self.updateMainView()

    def clickDecrBrightness(self):
        if self.checkboxAllViews.isChecked():
            for base in self.generator.bases:
                for color in self.colorSelectPanel.selectedColors():
                    base.changeBrightnessColor(-1, color)

            self.updatePreview(0)
            self.updatePreview(1)
            self.updatePreview(2)
            self.updatePreview(3)

        else:
            for color in self.colorSelectPanel.selectedColors():
                self.generator.base.changeBrightnessColor(-1, color)

        self.updateMainView()

    def clickSpriteControl(self, direction: str):
        if direction == 'left':
            self.generator.base.x -= 1
        elif direction == 'right':
            self.generator.base.x += 1
        elif direction == 'up':
            self.generator.base.y -= 1
        elif direction == 'down':
            self.generator.base.y += 1
        elif direction == 'leftright':
            self.generator.base.image = self.generator.base.image.transpose(
                Image.FLIP_LEFT_RIGHT)
        elif direction == 'updown':
            self.generator.base.image = self.generator.base.image.transpose(
                Image.FLIP_TOP_BOTTOM)

        self.updateMainView()

    def previewClicked(self, rot):
        old_rot = self.generator.current_rotation
        self.sprite_preview[old_rot].setStyleSheet(
            "background-color :  black; border:none;")
        self.sprite_preview[rot].setStyleSheet(
            "background-color :  black; border:2px outset green;")

        self.generator.rotationChanged(rot)

        self.updateMainView()

    def resetAllBases(self):
        self.generator.resetAllBases()

        self.updatePreview(0)
        self.updatePreview(1)
        self.updatePreview(2)
        self.updatePreview(3)
        self.previewClicked(0)

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
            self.labelDisplayName.setText(
                self.lineeditPrefix.text() + ' Fulltile ' + self.lineeditSuffix.text())
        else:
            self.labelDisplayName.setText(self.lineeditPrefix.text())

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
            self.listwidgetTemplateList.addItem(name)

    # Events

    def mousePressEvent(self, e):
        self.labelGenerateReturn.setText("")


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
