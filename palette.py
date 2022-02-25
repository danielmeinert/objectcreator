# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 11:56:19 2021

@author: Daniel
"""
import numpy as np
from PIL import Image
from palette_data import *


class Palette(np.ndarray):

    def __new__(cls, input_array, color_dict, has_sparkles=False):

        if has_sparkles:
            sparkles = input_array[19]
            input_array = input_array[0:19, :, :]
        obj = np.asarray(input_array).view(cls)
        obj.has_sparkles = has_sparkles
        obj.color_dict = color_dict
        if has_sparkles:
            obj.sparkles = sparkles

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.has_sparkles = getattr(obj, 'has_sparkles', None)
        self.sparkles = getattr(obj, 'sparkles', None)
        self.color_dict = getattr(obj, 'color_dict', None)

    # def __str__(self):
    #     return "Palette class"

    def __repr__(self):
        return "Palette class"

    def getColor(self, color: str):
        if color != 'Sparkles':
            if color not in self.color_dict.keys():
                raise KeyError(f'Color {color} not in palette')
            return self.__getitem__(self.color_dict[color])
        elif self.has_sparkles:
            return self.sparkles
        else:
            raise ValueError('Palette has no sparkles. Cannot return color.')

    def getRemapColor(self, color_name: str):
        color = np.zeros((12, 3))

        lookup = remap_lookup[remapColors()[color_name]]

        for i in range(12):
            color[i] = self[int(lookup[i][0]), int(lookup[i][1])]

        return color

    def arr(self):
        return np.array(self)


def allColors(sparkles=False):
    if not sparkles:
        return {
            'Grey': 0,
            'Dark Olive': 1,
            'Light Brown': 2,
            'Yellow': 3,
            'Bordeaux': 4,
            'Grass Green': 5,
            'Light Olive': 6,
            'Green': 7,
            'Tan': 8,
            'Indigo': 9,
            'Blue': 10,
            'Sea Green': 11,
            'Purple': 12,
            'Red': 13,
            'Orange': 14,
            'Teal': 15,
            'Pink': 16,
            'Brown': 17,
            '1st Remap': 18
        }
    else:
        return {
            'Grey': 0,
            'Dark Olive': 1,
            'Light Brown': 2,
            'Yellow': 3,
            'Bordeaux': 4,
            'Grass Green': 5,
            'Light Olive': 6,
            'Green': 7,
            'Tan': 8,
            'Indigo': 9,
            'Blue': 10,
            'Sea Green': 11,
            'Purple': 12,
            'Red': 13,
            'Orange': 14,
            'Teal': 15,
            'Pink': 16,
            'Brown': 17,
            '1st Remap': 18,
            'Sparkles': 19
        }


def remapColors():
    return {	'NoColor': -1,

             'Black': 0,
             'Grey': 1,
             'White': 2,
             'Dark Purple': 3,
             'Light Purple': 4,
             'Bright Purple': 5,
             'Dark Blue': 6,
             'Light Blue': 7,

             'Icy Blue': 8,
             'Dark Water': 9,
             'Light Water': 10,
             'Saturated Green': 11,
             'Dark Green': 12,
             'Moss Green': 13,
             'Bright Green': 14,
             'Olive Green': 15,

             'Dark Olive Green': 16,
             'Bright Yellow': 17,
             'Yellow': 18,
             'Dark Yellow': 19,
             'Light Orange': 20,
             'Dark Orange': 21,
             'Light Brown': 22,
             'Saturated Brown': 23,

             'Dark Brown': 24,
             'Salmon Pink': 25,
             'Bordeaux Red': 26,
             'Saturated Red': 27,
             'Bright Red': 28,
             'Dark Pink': 29,
             'Light Pink': 30,
             'Bright Pink': 31}


rct = Palette(rct_data, allColors(), has_sparkles=True)
orct = Palette(orct_data, allColors(), has_sparkles=True)
old_objm = Palette(old_objm_data, allColors(), has_sparkles=True)
save_colors = Palette(save_colors_data, save_colors_dict)


def switchPalette(image: Image.Image, pal_in: Palette, pal_out: Palette, include_sparkles=True):
    """Function to switch between given palettes.
    Input: image;    PIL image file you want to convert
           pal_in;   palette in (20,12,3) shape from which you want to convert
           pal_out;  palette in (20,12,3) shape to which you want to convert
    """

    data_in = np.array(image)
    data_out = np.array(data_in)

    if include_sparkles and not (pal_in.has_sparkles and pal_out.has_sparkles):
        raise ValueError(
            'Asked to include sparkles but one of given palette has no sparkles.')

    colors = allColors(include_sparkles).keys()

    for colorname in colors:
        color_old = pal_in.getColor(colorname)
        color_new = pal_out.getColor(colorname)

        for i in range(12):

            r1, g1, b1 = color_old[i]  # Original value
            r2, g2, b2 = color_new[i]  # Value that we want to replace it with
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)

# def generatePalette(image):


def addPalette(image, palette: Palette = orct, dither=True, include_sparkles=False):

    image = alphaToColor(image)
    image = image.convert('RGB')

    if include_sparkles and palette.has_sparkles:
        palette = np.concatenate(
            (np.array(palette), np.array([palette.sparkles])))
    elif include_sparkles:
        raise TypeError(
            'Asked to include sparkles but given palette has no sparkles.')

    pal_in = np.array(palette)

    pal_in = pal_in.reshape(-1, pal_in.shape[-1])
    pal_in = np.append(np.zeros((256-len(pal_in), 3)), pal_in, axis=0)
    pal_in = np.uint8(pal_in.flatten()).tolist()
    p = Image.new("P", (1, 1))
    p.putpalette(pal_in)
    image = image.quantize(method=3, palette=p,
                           dither=int(dither)).convert('RGBA')

    return removeBlackPixels(image)


def alphaToColor(image: Image.Image, color=(0, 0, 0)):
    """Set all fully transparent pixels of an RGBA image to the specified color.
    This is a very simple solution that might leave over some ugly edges, due
    to semi-transparent areas. You should use alpha_composite_with color instead.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    x = np.array(image)
    r, g, b, a = np.rollaxis(x, axis=-1)
    r[a == 0] = color[0]
    g[a == 0] = color[1]
    b[a == 0] = color[2]
    x = np.dstack([r, g, b, a])
    return Image.fromarray(x, 'RGBA')


def removeBlackPixels(image: Image.Image):
    data_in = np.array(image)
    data_out = np.array(data_in)
    r1, g1, b1 = (0, 0, 0)  # Original value
    red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    data_out[:, :, :][mask] = [0, 0, 0, 0]

    return Image.fromarray(data_out)
