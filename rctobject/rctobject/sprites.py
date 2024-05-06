# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2024 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""
import numpy as np
from PIL import Image
from copy import copy
import rctobject.palette as pal


class Sprite:
    def __init__(self, image: Image.Image, coords: tuple = None, palette: pal.Palette = pal.orct, dither: bool = True,
                 transparent_color: tuple = (0, 0, 0), include_sparkles=False, selected_colors=None, alpha_threshold=0):

        if image:
            image = pal.addPalette(
                image, palette, dither, transparent_color, include_sparkles, selected_colors, alpha_threshold)
        else:
            image = Image.new('RGBA', (1, 1))

        self.image = image
        self.image_base = image
        if coords:
            self.x, self.y = coords
            self.x_base, self.y_base = coords
        else:
            self.x = -int(image.size[0]/2)
            self.y = -int(image.size[1]/2)
            self.x_base = int(self.x)
            self.y_base = int(self.y)

        self.crop()
        self.palette = palette

    @classmethod
    def fromFile(cls, path: str, coords: tuple = None, palette: pal.Palette = pal.orct, dither: bool = True,
                 transparent_color: tuple = (0, 0, 0), include_sparkles=False, selected_colors=None, alpha_threshold=0):
        """Instantiates a new Sprite from an image file."""
        image = Image.open(path).convert('RGBA')
        return cls(
            image=image, coords=coords, palette=palette, dither=dither, transparent_color=transparent_color,
            include_sparkles=False, selected_colors=selected_colors, alpha_threshold=alpha_threshold)

    def save(self, path: str, keep_palette: bool = False):
        # Sprites should always be saved in the orct palette so that they can be read properly by the game
        if not keep_palette and self.palette is not pal.orct:
            self.switchPalette(pal.orct)
        self.image.save(path)

    def show(self, first_remap: str = 'NoColor', second_remap: str = 'NoColor', third_remap: str = 'NoColor'):
        return colorRemaps(self.image, first_remap, second_remap, third_remap)

    def giveProtectedPixelMask(self, color: str or list):
        return protectColorMask(self.image, color, self.palette)

    def resetSprite(self):
        self.image = self.image_base
        self.resetOffsets()

    def clearSprite(self):
        self.image = Image.new('RGBA', (1, 1))
        self.x, self.y, self.x_base, self.y_base = 0, 0, 0, 0

    def setFromSprite(self, sprite_in):
        self.image = copy(sprite_in.image)
        self.x = int(sprite_in.x)
        self.y = int(sprite_in.y)
        self.x_base = int(self.x)
        self.y_base = int(self.y)

    def resetOffsets(self):
        self.x = int(self.x_base)
        self.y = int(self.y_base)

    def overwriteOffsets(self, x, y):
        self.x = x
        self.y = y
        self.x_base = x
        self.y_base = y

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

    def removeColor(self, color: str or list):
        self.image = removeColor(self.image, color, self.palette)
        self.crop()

    def remapColor(self, color_name_old: str, color_name_new: str):
        self.image = remapColor(
            self.image, color_name_old, color_name_new,  self.palette)

    def colorAllInRemap(self, color_name: str):
        self.image = colorAllInRemap(self.image, color_name,  self.palette)

    def crop(self):
        bbox = self.image.getbbox()

        if bbox:
            self.image = self.image.crop(bbox)
            self.x = self.x + bbox[0]
            self.y = self.y + bbox[1]
        else:
            self.x = 0
            self.y = 0

    def merge(self, sprite, offset_x, offset_y):
        s1 = self
        s2 = sprite
        s2.x += offset_x
        s2.y += offset_y

        canvas_size_x = max(abs(s1.x), abs(s1.image.width+s1.x),
                            abs(s2.x), abs(s2.image.width+s2.x))
        canvas_size_y = max(abs(s1.y), abs(s1.image.height+s1.y),
                            abs(s2.y), abs(s2.image.height+s2.y))
        canvas = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))

        canvas.paste(s1.image, (s1.x+canvas_size_x, s1.y+canvas_size_y))
        canvas.paste(s2.image, (s2.x+canvas_size_x,
                     s2.y+canvas_size_y), mask=s2.image)

        bbox = canvas.getbbox()

        if bbox:
            canvas = canvas.crop(bbox)
            x_offset = -canvas_size_x + bbox[0]
            y_offset = -canvas_size_y + bbox[1]

            self.image = canvas
            self.x = x_offset
            self.y = y_offset

        self.crop()

    def giveShade(self, coords):
        if coords[0] < 0 or coords[1] < 0:
            return None

        try:
            r, g, b, a = self.image.getpixel(coords)
        except IndexError:
            return None

        if a == 0:
            return None

        try:
            arr = self.palette.arr()
            red, green, blue = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            truth_arr = (red == r) & (green == g) & (blue == b)
            index = list(truth_arr.flatten()).index(True)
            color = list(self.palette.color_dict.keys())[index//12]
            index = index % 12
        except ValueError:
            arr = self.palette.sparkles
            red, green, blue = arr[:, 0], arr[:, 1], arr[:, 2]
            truth_arr = (red == r) & (green == g) & (blue == b)
            index = list(truth_arr.flatten()).index(True)
            color = 'Sparkles'

        return (color, index)


def pasteOnMask(mask: Image.Image, pic_in: Image.Image):
    mask_ar = np.array(mask)
    pic_ar = np.array(pic_in)
    pic_ar[:, :, 3] = mask_ar[:, :, 3]
    return Image.fromarray(pic_ar)


def mergeSprites(image1: Image.Image, image2: Image.Image, palette: pal.Palette = pal.orct):
    im = Image.alpha_composite(image2, image1)
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
    colors = palette.getColor('2nd Remap')
    for color in colors:
        if np.equal(color, data[:, :, :3]).all(axis=2).any():
            return True

    return False


def checkTertiaryColor(image: Image.Image, palette: pal.Palette = pal.orct):
    data = np.array(image)
    colors = palette.getColor('3rd Remap')
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

    if 'Sparkles' in [color_name_old, color_name_new]:
        raise RuntimeError('Remapping of water sparkles not supported.')

    color_old = palette.getColor(color_name_old)
    color_new = palette.getColor(color_name_new)

    # if color_new == 'NoColor':
    #     return image

    for i in range(12):

        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :][mask] = [r2, g2, b2, 255]

    return Image.fromarray(data_out)


def colorRemaps(image: Image.Image, first_remap: str, second_remap: str, third_remap: str, palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    for color_names in [['1st Remap', first_remap], ['2nd Remap', second_remap], ['3rd Remap', third_remap]]:
        if color_names[1] == 'NoColor':
            continue

        color_old = palette.getColor(color_names[0])
        color_new = palette.getRemapColor(color_names[1])

        for i in range(12):

            r1, g1, b1 = color_old[i]  # Original value
            r2, g2, b2 = color_new[i]  # Value that we want to replace it with
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data_out[:, :, :3][mask] = [r2, g2, b2]

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

    color_old = palette.getColor('2nd Remap')
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

    color_old = palette.getColor('3rd Remap')
    color_new = palette.getRemapColor(color_name)

    for i in range(12):

        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)


def colorAllInRemap(image: Image.Image, color_name: str,  palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if color_name == 'NoColor':
        return image

    for color_old in pal.allColors():

        color_old = palette.getColor(color_old)
        color_new = palette.getRemapColor(color_name)

        for i in range(12):

            r1, g1, b1 = color_old[i]  # Original value
            r2, g2, b2 = color_new[i]  # Value that we want to replace it with
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)


def changeBrightnessColor(image: Image.Image, value: int, color: str or list, palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if isinstance(color, str):
        color = [color]

    for color_name in color:

        color = palette.getColor(color_name)

        if not isinstance(color, np.ndarray):
            continue

        if (value < 0):
            for step in range(-value):
                for i in range(len(color)):
                    j = i
                    if (i > 0):
                        j -= 1
                    r1, g1, b1 = color[i]  # Original value
                    # Value that we want to replace it with
                    r2, g2, b2 = color[j]
                    red, green, blue = data_in[:, :,
                                               0], data_in[:, :, 1], data_in[:, :, 2]
                    mask = (red == r1) & (green == g1) & (blue == b1)
                    data_out[:, :, :3][mask] = [r2, g2, b2]
        else:
            for step in range(value):
                for i in range(len(color)):
                    j = i
                    if (i < len(color) - 1):
                        j += 1
                    r1, g1, b1 = color[i]  # Original value
                    # Value that we want to replace it with
                    r2, g2, b2 = color[j]
                    red, green, blue = data_in[:, :,
                                               0], data_in[:, :, 1], data_in[:, :, 2]
                    mask = (red == r1) & (green == g1) & (blue == b1)
                    data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)


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

    mask = np.full(image.size, False).T

    if isinstance(color, str):
        color = [color]

    for color_name in color:

        if color_name not in palette.color_dict:
            continue
        color_arr = palette.getColor(color_name)

        for shade in color_arr:
            r1, g1, b1 = shade  # Original value
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = mask | ((red == r1) & (green == g1) & (blue == b1))

    data_out[:, :, :][mask] = [0, 0, 0, 0]

    return Image.fromarray(data_out)


def protectColorMask(image: Image.Image, color: str or list, palette: pal.Palette = pal.orct):
    data_in = np.array(image)

    mask = np.full(image.size, True).T

    if isinstance(color, str):
        color = [color]

    for color_name in color:

        if color_name not in palette.color_dict:
            continue
        color_arr = palette.getColor(color_name)

        for shade in color_arr:
            r1, g1, b1 = shade  # Original value
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = mask & ~((red == r1) & (green == g1) & (blue == b1))

    return Image.fromarray(~mask)
