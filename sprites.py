# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 23:40:34 2021

@author: Daniel
"""
import numpy as np
from PIL import Image
import palette as pal
import brightness as br


class sprite:
    def __init__(self, image: Image.Image, coords: tuple = (0, 0), palette: pal.Palette = pal.orct, dither: bool = True):
        if image:
            image = pal.addPalette(image, palette, dither)

        else:
            image = Image.new('RGBA', (1, 1))

        self.image = image
        self.image_base = image
        self.image_view = image
        self.x, self.y = coords
        self.palette = palette

    @classmethod
    def fromFile(cls, path: str, coords: tuple = (0, 0), palette: pal.Palette = pal.orct, dither: bool = True):
        """Instantiates a new Sprite from an image file."""
        image = Image.open(path).convert('RGBA')
        return cls(image=image, coords=coords, palette=palette, dither=dither)

    def save(self, path: str):
        self.image.save(path)

    def show(self, first_remap: str = 'NoColor', second_remap: str = 'NoColor'):
        image_view = self.image
        if first_remap != 'NoColor':
            image_view = colorFirstRemap(
                image_view, first_remap,  self.palette)
        if second_remap != 'NoColor':
            image_view = colorSecondRemap(
                image_view, first_remap,  self.palette)
        return image_view

    def resetSprite(self):
        self.image = self.image_base

    def removeBlackPixels(self):
        self.image = pal.removeBlackPixels(self.image)

    def checkPrimaryColor(self):
        return checkPrimaryColor(self.image, self.palette)

    def checkSecondaryColor(self):
        return checkSecondaryColor(self.image, self.palette)

    def checkColor(self, color_name: str):
        return checkColor(self.image, color_name, self.palette)

    def switchPalette(self, palette_new: pal.Palette, include_sparkles=True):
        self.image = pal.switchPalette(
            self.image, self.palette, palette_new, include_sparkles)

    def changeBrightness(self, step: int, include_sparkles: bool = False):
        self.image = br.changeBrightness(
            self.image, step, self.palette, include_sparkles)

    def changeBrightnessColor(self, step: int, color):
        self.image = br.changeBrightnessColor(
            self.image, step, color, self.palette)

    def remapColor(self, color_name_old: str, color_name_new: str):
        self.image = remapColor(
            self.image, color_name_old, color_name_new,  self.palette)

    def crop(self):
        bbox = self.image.getbbox()

        self.image = self.image.crop(bbox)
        self.x = self.x + bbox[0]
        self.y = self.y + bbox[1]


def pasteOnMask(mask: Image.Image, pic_in: Image.Image):
    mask_ar = np.array(mask)
    pic_ar = np.array(pic_in)
    pic_ar[:, :, 3] = mask_ar[:, :, 3]
    return Image.fromarray(pic_ar)


def mergeSprites(image1: Image.Image, image2: Image.Image, palette: pal.Palette = pal.orct):
    im = Image.alpha_composite(image2, image1)
    im = im.convert('RGB')
    im = pal.addPalette(im, palette, dither=True)
    return im


def checkPrimaryColor(image: Image.Image, palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette[18]
    for color in colors:
        if np.equal(color, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def checkSecondaryColor(image: Image.Image, palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette[16]
    for color in colors:
        if np.equal(color, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def checkColor(image: Image.Image, color_name: str,  palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette[pal.color_dict[color_name]]
    for shade in colors:
        if np.equal(shade, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def remapColor(image: Image.Image, color_name_old: str, color_name_new: str,  palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    color_old = palette.getColor(color_name_old)
    color_new = palette.getColor(color_name_new)

    for i in range(12):

        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :][mask] = [r2, g2, b2, 255]

    return Image.fromarray(data_out)


def colorFirstRemap(image: Image.Image, color_name: str,  palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if color_name == 'NoColor':
        return image

    color_old = palette.getColor('1st Remap')
    color_new = palette.getRemapColor(color_name)

    for i in range(12):

        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)


def colorSecondRemap(image: Image.Image, color_name: str,  palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if color_name == 'NoColor':
        return image

    color_old = palette.getColor('Pink')
    color_new = palette.getRemapColor(color_name)

    for i in range(12):

        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)
