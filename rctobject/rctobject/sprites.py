# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
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
                 transparent_color: tuple = (0, 0, 0), selected_colors: list = None, alpha_threshold: int = 0,
                 auto_offset_mode: str = 'bottom', offset: tuple = None, already_palettized: bool = False):

        if image:
            if not already_palettized:
                image = pal.addPalette(
                    image, palette, dither, transparent_color, selected_colors, alpha_threshold)
        else:
            image = Image.new('RGBA', (1, 1))

        self.image = image
        self.image_base = image
        if coords:
            self.x, self.y = coords
            self.x_base, self.y_base = coords
        else:
            if auto_offset_mode == 'bottom':
                self.x = -int(image.size[0]/2)
                self.y = -image.size[1]
            elif auto_offset_mode == 'center':
                self.x = -int(image.size[0]/2)
                self.y = -int(image.size[1]/2)
            else:
                self.x = 0
                self.y = 0

            if offset:
                self.x += offset[0]
                self.y += offset[1]

            self.x_base = int(self.x)
            self.y_base = int(self.y)

        self.crop()

        self.palette = palette

    @classmethod
    def fromFile(cls, path: str, coords: tuple = None, palette: pal.Palette = pal.orct, dither: bool = True,
                 transparent_color: tuple = (0, 0, 0), selected_colors: list = None, alpha_threshold: int = 0,
                 auto_offset_mode: str = 'bottom', offset: tuple = None, already_palettized: bool = False):
        """Instantiates a new Sprite from an image file."""
        image = Image.open(path).convert('RGBA')
        return cls(
            image=image, coords=coords, palette=palette, dither=dither, transparent_color=transparent_color,
            selected_colors=selected_colors, alpha_threshold=alpha_threshold, auto_offset_mode=auto_offset_mode, offset=offset, already_palettized=already_palettized)
        
    @classmethod
    def fromSprite(cls, sprite_in, offset: tuple = None):
        """Instantiates a new Sprite from another Sprite."""
        return cls(
            image=copy(sprite_in.image), coords=(sprite_in.x + (offset[0] if offset else 0), sprite_in.y + (offset[1] if offset else 0)), palette=sprite_in.palette, already_palettized=True)

    def save(self, path: str, keep_palette: bool = False, index_color=False):
        # Sprites should always be saved in the orct palette so that they can be read properly by the game
        if not keep_palette:
            if self.palette != pal.orct:
                self.switchPalette(pal.orct)

            if index_color:
                # We convert the image to an indexed image to optimize storage
                p = Image.new("P", (1, 1))
                p.putpalette(pal.complete_palette_array.flatten())

                image = self.image.convert('RGB').quantize(
                    palette=p)
                image.save(path, transparency=0)
            else:
                self.image.save(path)
        else:
            self.image.save(path)

    def isEmpty(self):
        return spriteIsEmpty(self)

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

    def switchPalette(self, palette_new: pal.Palette):
        self.image = pal.switchPalette(
            self.image, self.palette, palette_new)
        self.palette = palette_new

    def changeBrightness(self, step: int):
        self.image = changeBrightness(
            self.image, step, self.palette)

    def changeBrightnessColor(self, step: int, color):
        self.image = changeBrightnessColor(
            self.image, step, color, self.palette)

    def invertShadingColor(self, color: str or list):
        self.image = invertShadingColor(self.image, color, self.palette)

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
        
    def mask(self, sprite_mask, offset_x, offset_y):
        s1 = self
        s2 = sprite_mask
        s2.x += offset_x
        s2.y += offset_y

        canvas_size_x = max(abs(s1.x), abs(s1.image.width+s1.x),
                            abs(s2.x), abs(s2.image.width+s2.x))
        canvas_size_y = max(abs(s1.y), abs(s1.image.height+s1.y),
                            abs(s2.y), abs(s2.image.height+s2.y))
        canvas = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))
        mask = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))
        canvas.paste(s1.image, (s1.x+canvas_size_x, s1.y+canvas_size_y))
        mask.paste(s2.image, (s2.x+canvas_size_x, s2.y+canvas_size_y))
        
        canvas  = pasteOnMask(mask, canvas)
        
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

        return self.palette.giveShade(r, g, b, a)


def pasteOnMask(mask: Image.Image, pic_in: Image.Image):
    mask_ar = np.array(mask)
    pic_ar = np.array(pic_in)
    
    # Preserve alpha=0 regions in pic_in
    alpha_mask = pic_ar[:, :, 3] == 0
    pic_ar[:, :, 3] = np.where(alpha_mask, 0, mask_ar[:, :, 3])
    
    return Image.fromarray(pic_ar)


def mergeSprites(image1: Image.Image, image2: Image.Image, palette: pal.Palette = pal.orct, selected_colors: list = None):
    im = Image.alpha_composite(image2, image1)
    im = pal.addPalette(im, palette, dither=True, selected_colors=selected_colors)
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

    color_old = palette.getColor(color_name_old)
    color_new = palette.getColor(color_name_new)

    if color_name_old == 'Sparkles':
        color_old = np.append(
            color_old, [color_old[-1], color_old[-1]], axis=0)
    if color_name_new == 'Sparkles':
        color_new = np.append(
            color_new, [color_new[-1], color_new[-1]], axis=0)
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

        color_arr = palette.getColor(color_name)

        if not isinstance(color_arr, np.ndarray):
            continue

        if (value < 0):
            for step in range(-value):
                for i in range(len(color_arr)):
                    j = i
                    if (i > 0):
                        j -= 1
                    r1, g1, b1 = color_arr[i]  # Original value
                    # Value that we want to replace it with
                    r2, g2, b2 = color_arr[j]
                    red, green, blue = data_in[:, :,
                                               0], data_in[:, :, 1], data_in[:, :, 2]
                    mask = (red == r1) & (green == g1) & (blue == b1)
                    data_out[:, :, :3][mask] = [r2, g2, b2]
        else:
            for step in range(value):
                for i in range(len(color_arr)):
                    j = i
                    if (i < len(color_arr) - 1):
                        j += 1
                    r1, g1, b1 = color_arr[i]  # Original value
                    # Value that we want to replace it with
                    r2, g2, b2 = color_arr[j]
                    red, green, blue = data_in[:, :,
                                               0], data_in[:, :, 1], data_in[:, :, 2]
                    mask = (red == r1) & (green == g1) & (blue == b1)
                    data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)


def changeBrightness(image: Image.Image, step: int, palette: pal.Palette = pal.orct):

    if palette.has_sparkles:
        image = changeBrightnessColor(image, step, 'Sparkles', palette)

    image = changeBrightnessColor(
        image, step, list(palette.color_dict), palette)

    return image


def invertShadingColor(image: Image.Image, color: str or list, palette: pal.Palette = pal.orct):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if isinstance(color, str):
        color = [color]

    for color_name in color:

        color_arr = palette.getColor(color_name)

        if not isinstance(color_arr, np.ndarray):
            continue

        for i in range(len(color_arr)):

            r1, g1, b1 = color_arr[i]  # Original value
            # Value that we want to replace it with
            r2, g2, b2 = color_arr[len(color_arr)-1-i]
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data_out[:, :, :][mask] = [r2, g2, b2, 255]

    return Image.fromarray(data_out)


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


def spriteIsEmpty(sprite):
    if sprite.image.getbbox() is None:
        return True
    return False

