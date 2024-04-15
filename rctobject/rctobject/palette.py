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


class Palette(np.ndarray):

    def __new__(cls, input_array, color_dict, name, has_sparkles=False):

        if has_sparkles:
            sparkles = input_array[19]
            input_array = input_array[0:19, :, :]
        obj = np.asarray(input_array).view(cls)
        obj.has_sparkles = has_sparkles
        obj.color_dict = color_dict
        obj.name = name
        if has_sparkles:
            obj.sparkles = sparkles

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
            ret.append(self.getColor(color))

        return np.array(ret)

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

data = np.load(BytesIO(get_data("rctobject", "data/green_remap_pal.npy")))
green_remap = Palette(data, allColors(), 'green_remap', has_sparkles=True)

data = np.load(BytesIO(get_data("rctobject", "data/orct_pal.npy")))
orct = Palette(data, allColors(), 'orct', has_sparkles=True)

data = np.load(BytesIO(get_data("rctobject", "data/old_objm_pal.npy")))
old_objm = Palette(data, allColors(), 'old_objm', has_sparkles=True)

data = np.load(BytesIO(get_data("rctobject", "data/save_colors_pal.npy")))
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
save_colors = Palette(data, save_colors_dict, 'save_colors')

del (data)


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


def addPalette(image, palette: Palette = orct, dither=True, transparent_color=(0, 0, 0), include_sparkles=False, selected_colors=None, alpha_threshold=0):
    # If no transparent_color is given we choose the color from (0,0) pixel
    if not transparent_color:
        transparent_color = image.getpixel((0, 0))[:3]

    mask = alphaMask(image, transparent_color, alpha_threshold)
    image = image.convert('RGB')

    # If no selected_colors is given we use the entire palette
    if not selected_colors:
        selected_colors = palette.color_dict.keys()

    if include_sparkles and palette.has_sparkles:
        selected_colors.append('Sparkles')
    elif include_sparkles:
        raise TypeError(
            'Asked to include sparkles but given palette has no sparkles.')

    pal_in = palette.getReducedArray(selected_colors)

    pal_in = pal_in.reshape(-1, pal_in.shape[-1])
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


complete_palette_array = np.zeros((256, 3), dtype=int)

complete_palette_array[0] = np.array([0, 0, 0])
complete_palette_array[1] = np.array([0, 0, 0])
complete_palette_array[2] = np.array([0, 0, 0])
complete_palette_array[3] = np.array([0, 0, 0])
complete_palette_array[4] = np.array([0, 0, 0])
complete_palette_array[5] = np.array([0, 0, 0])
complete_palette_array[6] = np.array([0, 0, 0])
complete_palette_array[7] = np.array([0, 0, 0])
complete_palette_array[8] = np.array([0, 0, 0])
complete_palette_array[9] = np.array([0, 0, 0])
complete_palette_array[10] = np.array([23, 35, 35])
complete_palette_array[11] = np.array([35, 51, 51])
complete_palette_array[12] = np.array([47, 67, 67])
complete_palette_array[13] = np.array([63, 83, 83])
complete_palette_array[14] = np.array([75, 99, 99])
complete_palette_array[15] = np.array([91, 115, 115])
complete_palette_array[16] = np.array([111, 131, 131])
complete_palette_array[17] = np.array([131, 151, 151])
complete_palette_array[18] = np.array([159, 175, 175])
complete_palette_array[19] = np.array([183, 195, 195])
complete_palette_array[20] = np.array([211, 219, 219])
complete_palette_array[21] = np.array([239, 243, 243])
complete_palette_array[22] = np.array([51, 47, 0])
complete_palette_array[23] = np.array([63, 59, 0])
complete_palette_array[24] = np.array([79, 75, 11])
complete_palette_array[25] = np.array([91, 91, 19])
complete_palette_array[26] = np.array([107, 107, 31])
complete_palette_array[27] = np.array([119, 123, 47])
complete_palette_array[28] = np.array([135, 139, 59])
complete_palette_array[29] = np.array([151, 155, 79])
complete_palette_array[30] = np.array([167, 175, 95])
complete_palette_array[31] = np.array([187, 191, 115])
complete_palette_array[32] = np.array([203, 207, 139])
complete_palette_array[33] = np.array([223, 227, 163])
complete_palette_array[34] = np.array([67, 43, 7])
complete_palette_array[35] = np.array([87, 59, 11])
complete_palette_array[36] = np.array([111, 75, 23])
complete_palette_array[37] = np.array([127, 87, 31])
complete_palette_array[38] = np.array([143, 99, 39])
complete_palette_array[39] = np.array([159, 115, 51])
complete_palette_array[40] = np.array([179, 131, 67])
complete_palette_array[41] = np.array([191, 151, 87])
complete_palette_array[42] = np.array([203, 175, 111])
complete_palette_array[43] = np.array([219, 199, 135])
complete_palette_array[44] = np.array([231, 219, 163])
complete_palette_array[45] = np.array([247, 239, 195])
complete_palette_array[46] = np.array([71, 27, 0])
complete_palette_array[47] = np.array([95, 43, 0])
complete_palette_array[48] = np.array([119, 63, 0])
complete_palette_array[49] = np.array([143, 83, 7])
complete_palette_array[50] = np.array([167, 111, 7])
complete_palette_array[51] = np.array([191, 139, 15])
complete_palette_array[52] = np.array([215, 167, 19])
complete_palette_array[53] = np.array([243, 203, 27])
complete_palette_array[54] = np.array([255, 231, 47])
complete_palette_array[55] = np.array([255, 243, 95])
complete_palette_array[56] = np.array([255, 251, 143])
complete_palette_array[57] = np.array([255, 255, 195])
complete_palette_array[58] = np.array([35, 0, 0])
complete_palette_array[59] = np.array([79, 0, 0])
complete_palette_array[60] = np.array([95, 7, 7])
complete_palette_array[61] = np.array([111, 15, 15])
complete_palette_array[62] = np.array([127, 27, 27])
complete_palette_array[63] = np.array([143, 39, 39])
complete_palette_array[64] = np.array([163, 59, 59])
complete_palette_array[65] = np.array([179, 79, 79])
complete_palette_array[66] = np.array([199, 103, 103])
complete_palette_array[67] = np.array([215, 127, 127])
complete_palette_array[68] = np.array([235, 159, 159])
complete_palette_array[69] = np.array([255, 191, 191])
complete_palette_array[70] = np.array([27, 51, 19])
complete_palette_array[71] = np.array([35, 63, 23])
complete_palette_array[72] = np.array([47, 79, 31])
complete_palette_array[73] = np.array([59, 95, 39])
complete_palette_array[74] = np.array([71, 111, 43])
complete_palette_array[75] = np.array([87, 127, 51])
complete_palette_array[76] = np.array([99, 143, 59])
complete_palette_array[77] = np.array([115, 155, 67])
complete_palette_array[78] = np.array([131, 171, 75])
complete_palette_array[79] = np.array([147, 187, 83])
complete_palette_array[80] = np.array([163, 203, 95])
complete_palette_array[81] = np.array([183, 219, 103])
complete_palette_array[82] = np.array([31, 55, 27])
complete_palette_array[83] = np.array([47, 71, 35])
complete_palette_array[84] = np.array([59, 83, 43])
complete_palette_array[85] = np.array([75, 99, 55])
complete_palette_array[86] = np.array([91, 111, 67])
complete_palette_array[87] = np.array([111, 135, 79])
complete_palette_array[88] = np.array([135, 159, 95])
complete_palette_array[89] = np.array([159, 183, 111])
complete_palette_array[90] = np.array([183, 207, 127])
complete_palette_array[91] = np.array([195, 219, 147])
complete_palette_array[92] = np.array([207, 231, 167])
complete_palette_array[93] = np.array([223, 247, 191])
complete_palette_array[94] = np.array([15, 63, 0])
complete_palette_array[95] = np.array([19, 83, 0])
complete_palette_array[96] = np.array([23, 103, 0])
complete_palette_array[97] = np.array([31, 123, 0])
complete_palette_array[98] = np.array([39, 143, 7])
complete_palette_array[99] = np.array([55, 159, 23])
complete_palette_array[100] = np.array([71, 175, 39])
complete_palette_array[101] = np.array([91, 191, 63])
complete_palette_array[102] = np.array([111, 207, 87])
complete_palette_array[103] = np.array([139, 223, 115])
complete_palette_array[104] = np.array([163, 239, 143])
complete_palette_array[105] = np.array([195, 255, 179])
complete_palette_array[106] = np.array([79, 43, 19])
complete_palette_array[107] = np.array([99, 55, 27])
complete_palette_array[108] = np.array([119, 71, 43])
complete_palette_array[109] = np.array([139, 87, 59])
complete_palette_array[110] = np.array([167, 99, 67])
complete_palette_array[111] = np.array([187, 115, 83])
complete_palette_array[112] = np.array([207, 131, 99])
complete_palette_array[113] = np.array([215, 151, 115])
complete_palette_array[114] = np.array([227, 171, 131])
complete_palette_array[115] = np.array([239, 191, 151])
complete_palette_array[116] = np.array([247, 207, 171])
complete_palette_array[117] = np.array([255, 227, 195])
complete_palette_array[118] = np.array([15, 19, 55])
complete_palette_array[119] = np.array([39, 43, 87])
complete_palette_array[120] = np.array([51, 55, 103])
complete_palette_array[121] = np.array([63, 67, 119])
complete_palette_array[122] = np.array([83, 83, 139])
complete_palette_array[123] = np.array([99, 99, 155])
complete_palette_array[124] = np.array([119, 119, 175])
complete_palette_array[125] = np.array([139, 139, 191])
complete_palette_array[126] = np.array([159, 159, 207])
complete_palette_array[127] = np.array([183, 183, 223])
complete_palette_array[128] = np.array([211, 211, 239])
complete_palette_array[129] = np.array([239, 239, 255])
complete_palette_array[130] = np.array([0, 27, 111])
complete_palette_array[131] = np.array([0, 39, 151])
complete_palette_array[132] = np.array([7, 51, 167])
complete_palette_array[133] = np.array([15, 67, 187])
complete_palette_array[134] = np.array([27, 83, 203])
complete_palette_array[135] = np.array([43, 103, 223])
complete_palette_array[136] = np.array([67, 135, 227])
complete_palette_array[137] = np.array([91, 163, 231])
complete_palette_array[138] = np.array([119, 187, 239])
complete_palette_array[139] = np.array([143, 211, 243])
complete_palette_array[140] = np.array([175, 231, 251])
complete_palette_array[141] = np.array([215, 247, 255])
complete_palette_array[142] = np.array([11, 43, 15])
complete_palette_array[143] = np.array([15, 55, 23])
complete_palette_array[144] = np.array([23, 71, 31])
complete_palette_array[145] = np.array([35, 83, 43])
complete_palette_array[146] = np.array([47, 99, 59])
complete_palette_array[147] = np.array([59, 115, 75])
complete_palette_array[148] = np.array([79, 135, 95])
complete_palette_array[149] = np.array([99, 155, 119])
complete_palette_array[150] = np.array([123, 175, 139])
complete_palette_array[151] = np.array([147, 199, 167])
complete_palette_array[152] = np.array([175, 219, 195])
complete_palette_array[153] = np.array([207, 243, 223])
complete_palette_array[154] = np.array([63, 0, 95])
complete_palette_array[155] = np.array([75, 7, 115])
complete_palette_array[156] = np.array([83, 15, 127])
complete_palette_array[157] = np.array([95, 31, 143])
complete_palette_array[158] = np.array([107, 43, 155])
complete_palette_array[159] = np.array([123, 63, 171])
complete_palette_array[160] = np.array([135, 83, 187])
complete_palette_array[161] = np.array([155, 103, 199])
complete_palette_array[162] = np.array([171, 127, 215])
complete_palette_array[163] = np.array([191, 155, 231])
complete_palette_array[164] = np.array([215, 195, 243])
complete_palette_array[165] = np.array([243, 235, 255])
complete_palette_array[166] = np.array([63, 0, 0])
complete_palette_array[167] = np.array([87, 0, 0])
complete_palette_array[168] = np.array([115, 0, 0])
complete_palette_array[169] = np.array([143, 0, 0])
complete_palette_array[170] = np.array([171, 0, 0])
complete_palette_array[171] = np.array([199, 0, 0])
complete_palette_array[172] = np.array([227, 7, 0])
complete_palette_array[173] = np.array([255, 7, 0])
complete_palette_array[174] = np.array([255, 79, 67])
complete_palette_array[175] = np.array([255, 123, 115])
complete_palette_array[176] = np.array([255, 171, 163])
complete_palette_array[177] = np.array([255, 219, 215])
complete_palette_array[178] = np.array([79, 39, 0])
complete_palette_array[179] = np.array([111, 51, 0])
complete_palette_array[180] = np.array([147, 63, 0])
complete_palette_array[181] = np.array([183, 71, 0])
complete_palette_array[182] = np.array([219, 79, 0])
complete_palette_array[183] = np.array([255, 83, 0])
complete_palette_array[184] = np.array([255, 111, 23])
complete_palette_array[185] = np.array([255, 139, 51])
complete_palette_array[186] = np.array([255, 163, 79])
complete_palette_array[187] = np.array([255, 183, 107])
complete_palette_array[188] = np.array([255, 203, 135])
complete_palette_array[189] = np.array([255, 219, 163])
complete_palette_array[190] = np.array([0, 51, 47])
complete_palette_array[191] = np.array([0, 63, 55])
complete_palette_array[192] = np.array([0, 75, 67])
complete_palette_array[193] = np.array([0, 87, 79])
complete_palette_array[194] = np.array([7, 107, 99])
complete_palette_array[195] = np.array([23, 127, 119])
complete_palette_array[196] = np.array([43, 147, 143])
complete_palette_array[197] = np.array([71, 167, 163])
complete_palette_array[198] = np.array([99, 187, 187])
complete_palette_array[199] = np.array([131, 207, 207])
complete_palette_array[200] = np.array([171, 231, 231])
complete_palette_array[201] = np.array([207, 255, 255])
complete_palette_array[202] = np.array([63, 0, 27])
complete_palette_array[203] = np.array([103, 0, 51])
complete_palette_array[204] = np.array([123, 11, 63])
complete_palette_array[205] = np.array([143, 23, 79])
complete_palette_array[206] = np.array([163, 31, 95])
complete_palette_array[207] = np.array([183, 39, 111])
complete_palette_array[208] = np.array([219, 59, 143])
complete_palette_array[209] = np.array([239, 91, 171])
complete_palette_array[210] = np.array([243, 119, 187])
complete_palette_array[211] = np.array([247, 151, 203])
complete_palette_array[212] = np.array([251, 183, 223])
complete_palette_array[213] = np.array([255, 215, 239])
complete_palette_array[214] = np.array([39, 19, 0])
complete_palette_array[215] = np.array([55, 31, 7])
complete_palette_array[216] = np.array([71, 47, 15])
complete_palette_array[217] = np.array([91, 63, 31])
complete_palette_array[218] = np.array([107, 83, 51])
complete_palette_array[219] = np.array([123, 103, 75])
complete_palette_array[220] = np.array([143, 127, 107])
complete_palette_array[221] = np.array([163, 147, 127])
complete_palette_array[222] = np.array([187, 171, 147])
complete_palette_array[223] = np.array([207, 195, 171])
complete_palette_array[224] = np.array([231, 219, 195])
complete_palette_array[225] = np.array([255, 243, 223])
complete_palette_array[226] = np.array([55, 75, 75])
complete_palette_array[227] = np.array([255, 183, 0])
complete_palette_array[228] = np.array([255, 219, 0])
complete_palette_array[229] = np.array([255, 255, 0])
complete_palette_array[230] = np.array([39, 143, 135])
complete_palette_array[231] = np.array([7, 107, 99])
complete_palette_array[232] = np.array([7, 107, 99])
complete_palette_array[233] = np.array([7, 107, 99])
complete_palette_array[234] = np.array([27, 131, 123])
complete_palette_array[235] = np.array([155, 227, 227])
complete_palette_array[236] = np.array([55, 155, 151])
complete_palette_array[237] = np.array([55, 155, 151])
complete_palette_array[238] = np.array([55, 155, 151])
complete_palette_array[239] = np.array([115, 203, 203])
complete_palette_array[240] = np.array([67, 91, 91])
complete_palette_array[241] = np.array([83, 107, 107])
complete_palette_array[242] = np.array([99, 123, 123])
complete_palette_array[243] = np.array([111, 51, 47])
complete_palette_array[244] = np.array([131, 55, 47])
complete_palette_array[245] = np.array([151, 63, 51])
complete_palette_array[246] = np.array([171, 67, 51])
complete_palette_array[247] = np.array([191, 75, 47])
complete_palette_array[248] = np.array([211, 79, 43])
complete_palette_array[249] = np.array([231, 87, 35])
complete_palette_array[250] = np.array([255, 95, 31])
complete_palette_array[251] = np.array([255, 127, 39])
complete_palette_array[252] = np.array([255, 155, 51])
complete_palette_array[253] = np.array([255, 183, 63])
complete_palette_array[254] = np.array([255, 207, 75])
complete_palette_array[255] = np.array([0, 0, 0])
