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
from io import BytesIO
from pkgutil import get_data

import rctobject.palette_data as palette_data


class Palette(np.ndarray):

    def __new__(cls, input_array, color_dict, name, sparkles_data=None):

        obj = np.asarray(input_array).view(cls)
        obj.has_sparkles = isinstance(sparkles_data, np.ndarray)
        obj.color_dict = color_dict
        obj.name = name
        if obj.has_sparkles:
            obj.sparkles = sparkles_data
        else:
            obj.sparkles = None

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.has_sparkles = getattr(obj, 'has_sparkles', None)
        self.sparkles = getattr(obj, 'sparkles', None)
        self.color_dict = getattr(obj, 'color_dict', None)
        self.name = getattr(obj, 'name', None)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    # def __repr__(self):
    #     return str(self.name)

    def getColor(self, color: str):
        if color == 'Pink':
            color = '2nd Remap'
        elif color == 'Yellow':
            color = '3rd Remap'

        if color != 'Sparkles':
            i = self.color_dict.get(color, -1)
            if i > -1:
                return self.__getitem__(i)
        elif self.has_sparkles:
            return self.sparkles

        return None

    def getRemapColor(self, color_name: str):
        if color_name == '1st Remap':
            return self.getColor(color_name)

        color = np.zeros((12, 3), dtype='uint8')

        lookup = remap_lookup[remapColors()[color_name]]

        for i in range(12):
            color[i] = self[int(lookup[i][0]), int(lookup[i][1])]

        return color

    def getReducedArray(self, colors: list):
        ret = []
        for color in colors:
            if color != 'Sparkles':
                ret.append(self.getColor(color))

        return np.array(ret)

    def getColorNearest(self, target_color):
        """Get the nearest color in the palette to a given target color.

        Args:
            target_color (array-like): The target color values.

        Returns:
            array-like: The color values from the palette.
        """
        # Reshape the palette to a 2D array
        palette_flat = self.reshape(-1, 3)

        # Calculate the Euclidean distance between the target color and all colors in the palette
        distances = np.linalg.norm(palette_flat - target_color, axis=1)

        # Find the index of the color with the minimum distance
        nearest_index = np.argmin(distances)

        # Get the nearest color from the palette
        nearest_color = tuple(palette_flat[nearest_index])

        return nearest_color

    def arr(self):
        return np.array(self)


def allColors(sparkles=False):
    if not sparkles:
        return {
            'Grey': 0,
            'Dark Olive': 1,
            'Light Brown': 2,
            '3rd Remap': 3,
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
            '2nd Remap': 16,
            'Brown': 17,
            '1st Remap': 18
        }
    else:
        return {
            'Grey': 0,
            'Dark Olive': 1,
            'Light Brown': 2,
            '3rd Remap': 3,
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
            '2nd Remap': 16,
            'Brown': 17,
            '1st Remap': 18,
            'Sparkles': 19
        }


def remapColors():
    return {'NoColor': -1,

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


remap_lookup = np.load(
    BytesIO(get_data("rctobject", "data/remap_mapping.npy"))).astype('uint8')

complete_palette_array = palette_data.complete_palette_array

green_remap = Palette(palette_data.rct_data, allColors(), 'green_remap',
                      sparkles_data=palette_data.original_sparkles_data)

orct = Palette(palette_data.orct_data, allColors(), 'orct',
               sparkles_data=palette_data.orct_sparkles_data)

old_objm = Palette(palette_data.old_objm_data, allColors(), 'old_objm',
                   sparkles_data=palette_data.original_sparkles_data)

save_colors_dict = {
    'Grey': 0,
    'Light Brown': 1,
    'Yellow': 2,
    'Bordeaux': 3,
    'Grass Green': 4,
    'Light Olive': 5,
    'Tan': 6,
    'Blue': 7,
    'Sea Green': 8,
    'Teal': 10,
    'Brown': 11

}
save_colors = Palette(palette_data.save_colors_data,
                      save_colors_dict, 'save_colors')


def switchPalette(image: Image.Image, pal_in: Palette, pal_out: Palette):
    """Function to switch between given palettes.
    Input: image;    PIL image file you want to convert
           pal_in;   palette in (20,12,3) shape from which you want to convert
           pal_out;  palette in (20,12,3) shape to which you want to convert
    """

    data_in = np.array(image)
    data_out = np.array(data_in)

    include_sparkles = pal_in.has_sparkles and pal_out.has_sparkles

    colors = allColors(include_sparkles).keys()

    for colorname in colors:
        color_old = pal_in.getColor(colorname)
        color_new = pal_out.getColor(colorname)

        for i in range(len(color_old)):

            r1, g1, b1 = color_old[i]  # Original value
            r2, g2, b2 = color_new[i]  # Value that we want to replace it with
            red, green, blue = data_in[:, :,
                                       0], data_in[:, :, 1], data_in[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data_out[:, :, :3][mask] = [r2, g2, b2]

    return Image.fromarray(data_out)

# def generatePalette(image):


def addPalette(image, palette: Palette = orct, dither=True, transparent_color=(0, 0, 0), selected_colors=None, alpha_threshold=0):
    # If no transparent_color is given we choose the color from (0,0) pixel
    if not transparent_color:
        transparent_color = image.getpixel((0, 0))[:3]

    mask = alphaMask(image, transparent_color, alpha_threshold)
    image = image.convert('RGB')

    # If no selected_colors is given we use the entire palette
    if not selected_colors:
        selected_colors = list(palette.color_dict.keys())
        if palette.has_sparkles:
            selected_colors.append('Sparkles')

    pal_in = palette.getReducedArray(selected_colors)

    if pal_in.size > 0:
        pal_in = pal_in.reshape(-1, pal_in.shape[-1])
    else:
        pal_in = np.array([])

    if 'Sparkles' in selected_colors and palette.has_sparkles:
        pal_in = np.concatenate((pal_in, palette.sparkles))
    elif 'Sparkles' in selected_colors:
        raise RuntimeError(
            'Asked to include sparkles but given palette has no sparkles.')

    pal_in = np.append(np.zeros((256-len(pal_in), 3)), pal_in, axis=0)
    pal_in = np.uint8(pal_in.flatten()).tolist()
    p = Image.new("P", (1, 1))
    p.putpalette(pal_in)
    image = image.quantize(method=3, palette=p,
                           dither=int(dither)).convert('RGBA')

    return removeColorOnMask(image, mask)


def alphaToColor(image: Image.Image, color=(0, 0, 0)):
    """Set all fully transparent pixels of an RGBA image to the specified color.
    This is a very simple solution that might leave over some ugly edges, due
    to semi-transparent areas. You should use alpha_composite_with color instead.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 0, 0, 0)

    """
    x = np.array(image)
    r, g, b, a = np.rollaxis(x, axis=-1)
    r[a == 0] = color[0]
    g[a == 0] = color[1]
    b[a == 0] = color[2]
    x = np.dstack([r, g, b, a])
    return Image.fromarray(x, 'RGBA')


def colorAllVisiblePixels(image: Image.Image, color):
    x = np.array(image)
    r, g, b, a = np.rollaxis(x, axis=-1)
    r[a != 0] = color[0]
    g[a != 0] = color[1]
    b[a != 0] = color[2]
    x = np.dstack([r, g, b, a])
    return Image.fromarray(x, 'RGBA')


def alphaMask(image: Image.Image, color=(0, 0, 0), alpha_threshold=0):
    data_in = np.array(image)
    r1, g1, b1 = color

    red, green, blue, alpha = data_in[:, :, 0], data_in[:,
                                                        :, 1], data_in[:, :, 2], data_in[:, :, 3]
    mask = ((red == r1) & (green == g1) & (
        blue == b1)) | (alpha <= alpha_threshold)

    return mask


def removeColorWhenImport(image: Image.Image, color=(0, 0, 0)):
    data_in = np.array(image)
    data_out = np.array(data_in)

    if color:
        r1, g1, b1 = color
    else:
        r1, g1, b1 = data_in[0, 0][:3]

    red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    data_out[:, :, :][mask] = [0, 0, 0, 0]

    return Image.fromarray(data_out)


def removeColorOnMask(image: Image.Image, mask: np.array):
    data = np.array(image)

    data[:, :, :][mask] = [0, 0, 0, 0]

    return Image.fromarray(data)


def floydSteinbergDithering(image: Image.Image, palette: Palette):
    """Apply Floyd-Steinberg dithering to a color image using a specified palette.

    Args:
        image (PIL.Image.Image): The input color image.
        palette (Palette): The palette to use for dithering.

    Returns:
        PIL.Image.Image: The dithered color image.
    """
    # Convert the image to RGB mode if not already
    image = image.convert("RGB")
    # Convert the image to numpy array
    input_array = np.array(image)
    # Create an empty output array to store the dithered image
    output_array = np.zeros_like(input_array, dtype=np.uint8)

    # Iterate over each pixel in the image
    for y in range(input_array.shape[0]):
        for x in range(input_array.shape[1]):
            # Get the original pixel values
            old_pixel = input_array[y, x]
            # Get the nearest color from the palette
            new_pixel = palette.getColorNearest(old_pixel)
            # Set the output pixel value
            output_array[y, x] = new_pixel
            # Calculate the quantization error
            error = old_pixel - new_pixel
            # Ensure error has the same dtype as input_array
            error = error.astype(input_array.dtype)
            # Diffuse the error to neighboring pixels
            if x < input_array.shape[1] - 1:
                # Ensure the diffusion operation also has the same dtype as input_array
                input_array[y, x + 1] += (error * np.array([7/16,
                                          7/16, 7/16])).astype(input_array.dtype)
            if y < input_array.shape[0] - 1:
                if x > 0:
                    input_array[y + 1, x - 1] += (error * np.array(
                        [3/16, 3/16, 3/16])).astype(input_array.dtype)
                input_array[y + 1, x] += (error * np.array([5/16,
                                          5/16, 5/16])).astype(input_array.dtype)
                if x < input_array.shape[1] - 1:
                    input_array[y + 1, x + 1] += (error * np.array(
                        [1/16, 1/16, 1/16])).astype(input_array.dtype)

    # Convert the output array back to an image
    dithered_image = Image.fromarray(output_array, mode="RGB")

    return dithered_image
