# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 23:40:34 2021

@author: Daniel
"""
import numpy as np
from PIL import Image
import rctobject.palette as pal


class Sprite:
    def __init__(self, image: Image.Image, coords: tuple = (0, 0), palette: pal.Palette = pal.orct, dither: bool = True, use_transparency: bool = False, transparent_color: tuple = None):
        
        if image:
            if use_transparency:
                image = pal.removeColorWhenImport(image, transparent_color) 
                
            image = pal.addPalette(image, palette, dither)
            
        else:
            image = Image.new('RGBA', (1, 1))

        self.image = image
        self.image_base = image
        self.x, self.y = coords
        self.x_base, self.y_base = coords
        self.palette = palette

    @classmethod
    def fromFile(cls, path: str, coords: tuple = (0, 0), palette: pal.Palette = pal.orct, dither: bool = True, use_transparency: bool = False, transparent_color: tuple = None):
        """Instantiates a new Sprite from an image file."""
        image = Image.open(path).convert('RGBA')
        return cls(image=image, coords=coords, palette=palette, dither=dither, use_transparency = use_transparency, transparent_color = transparent_color)

    def save(self, path: str, keep_palette: bool = False):
        # Sprites should always be saved in the orct palette so that they can be read properly by the game
        if not keep_palette and self.palette is not pal.orct:
            self.switchPalette(pal.orct)
        self.image.save(path)

    def show(self, first_remap: str = 'NoColor', second_remap: str = 'NoColor', third_remap: str = 'NoColor'):
        image_view = self.image
        if first_remap != 'NoColor':
            image_view = colorFirstRemap(
                image_view, first_remap,  self.palette)
        if second_remap != 'NoColor':
            image_view = colorSecondRemap(
                image_view, second_remap,  self.palette)
        if third_remap != 'NoColor':
            image_view = colorThirdRemap(
                image_view, third_remap,  self.palette)
        return image_view

    def resetSprite(self):
        self.image = self.image_base
        
    def resetOffsets(self):
        self.x = int(self.x_base)
        self.y = int(self.y_base)

    def removeBlackPixels(self):
        self.image = pal.removeBlackPixels(self.image)

    def checkPrimaryColor(self):
        return checkPrimaryColor(self.image, self.palette)

    def checkSecondaryColor(self):
        return checkSecondaryColor(self.image, self.palette)

    def checkTertiaryColor(self):
        return checkTertiaryColor(self.image, self.palette)

    def checkColor(self, color_name: str):
        return checkColor(self.image, color_name, self.palette)

    def switchPalette(self, palette_new: pal.Palette, include_sparkles=True):
        self.image = pal.switchPalette(
            self.image, self.palette, palette_new, include_sparkles)
        self.palette = palette_new


    def changeBrightness(self, step: int, include_sparkles: bool = False):
        self.image = changeBrightness(
            self.image, step, self.palette, include_sparkles)

    def changeBrightnessColor(self, step: int, color):
        self.image = changeBrightnessColor(
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
    colors = palette.getColor('1st Remap')
    for color in colors:
        if np.equal(color, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def checkSecondaryColor(image: Image.Image, palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette.getColor('Pink')
    for color in colors:
        if np.equal(color, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def checkTertiaryColor(image: Image.Image, palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette.getColor('Yellow')
    for color in colors:
        if np.equal(color, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def checkColor(image: Image.Image, color_name: str,  palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette.getColor(color_name)
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


def colorThirdRemap(image: Image.Image, color_name: str,  palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if color_name == 'NoColor':
        return image

    color_old = palette.getColor('Yellow')
    color_new = palette.getRemapColor(color_name)

    for i in range(12):

        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)


def _decrBr(data_in, color):
    data_out = np.array(data_in)

    for i in range(12):
        j = i
        if(i > 0):
            j -= 1
        r1, g1, b1 = color[i]  # Original value
        r2, g2, b2 = color[j]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]

    return data_out


def _incrBr(data_in, color):
    data_out = np.array(data_in)

    for i in range(12):
        j = i
        if(i < 11):
            j += 1
        r1, g1, b1 = color[i]  # Original value
        r2, g2, b2 = color[j]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]

    return data_out


def changeBrightnessColor(image: Image.Image, step: int, color: str or list, palette: pal.Palette = pal.orct):
    data = np.array(image)

    if isinstance(color, str):
        color = [color]
    
    for color_name in color:
    
        if color_name not in palette.color_dict:
            continue
    
        color_arr = palette.getColor(color_name)
        
        if(step < 0):
            for i in range(-step):
                data = _decrBr(data, color_arr)
        else:
            for i in range(step):
                data = _incrBr(data, color_arr)

    return Image.fromarray(data)


def changeBrightness(image: Image.Image, step: int, palette: pal.Palette = pal.orct, include_sparkles=False):

    if include_sparkles and palette.has_sparkles:
        image = changeBrightnessColor(image, step, 'Sparkles', palette)
    elif include_sparkles:
        raise TypeError(
            'Asked to include sparkles but given palette has no sparkles.')

    image = changeBrightnessColor(
        image, step, list(palette.color_dict), palette)

    return image


def removeColor(image: Image.Image, color: str or list, palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)
    
    if isinstance(color, str):
        color = [color]
    
    for color_name in color:
    
        if color_name not in palette.color_dict:
            continue
        color_arr = palette.getColor(color_name)
        
        for shade in color_arr:
            r1, g1, b1 = shade  # Original value
            red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data_out[:, :, :][mask] = [0, 0, 0, 0]

    return Image.fromarray(data_out)