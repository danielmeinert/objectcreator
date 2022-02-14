# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 23:40:34 2021

@author: Daniel
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 16:41:33 2021

@author: Daniel
"""

import numpy as np
from PIL import Image
import palette as pal
import brightness as br




class sprite:
    def __init__(self, image : Image.Image, palette : pal.Palette = pal.orct, dither : bool = True):
        self.image = pal.addPalette(image, palette, dither)
        self.image_base = pal.addPalette(image, palette, dither)
        self.image_view = pal.addPalette(image, palette, dither)
        self.x = 0
        self.y = 0
        self.palette = palette
        self.current_first_remap = 'NoColor'
        self.current_second_remap = 'NoColor'
        
    
    def resetSprite(self):
        self.image = self.image_base
        self.image_view = self.image_base
        
    def removeBlackPixels(self):
        self.image = removeBlackPixels(self.image)
        
    def checkPrimaryColor(self):
        return checkPrimaryColor(self.image, self.palette)       
    
    def checkSecondaryColor(self):
        return checkSecondaryColor(self.image, self.palette)
    
    def checkColor(self, color_name : str):
        return checkColor(self.image,color_name, self.palette)
           
    def switchPalette(self, palette_new : pal.Palette, include_sparkles = True):
        self.image = pal.switchPalette(self.image, self.palette, palette_new, include_sparkles)

    def changeBrightness(self, step : int, include_sparkles : bool = False):
        self.image = br.changeBrightness(self.image, step, self.palette, include_sparkles)
        
    def changeBrightnessColor(self, step : int, color):
        self.image = br.changeBrightnessColor(self.image, step,color, self.palette)
        
    def colorFirstRemap(self, color_name : str, remap_colors : pal.Palette = pal.ingame_remaps):
        self.image.current_first_remap = color_name
        self.image_view = colorFirstRemap(self.image, color_name,  self.palette, remap_colors)

    def colorSecondRemap(self, color_name : str, remap_colors : pal.Palette = pal.ingame_remaps):
        self.image.current_second_remap = color_name
        self.image_view = colorSecondRemap(self.image, color_name,  self.palette, remap_colors)

def pasteOnMask(mask : Image.Image,pic_in : Image.Image):
    mask_ar = np.array(mask)
    pic_ar = np.array(pic_in)
    pic_ar[:,:,3] = mask_ar[:,:,3]
    return Image.fromarray(pic_ar)
                        
def mergeSprites(sprite1 : Image.Image,sprite2 : Image.Image, palette : pal.Palette = pal.orct):
    im = Image.alpha_composite(sprite2, sprite1)
    im = im.convert('RGB')
    im = pal.addPalette(im,palette, dither = True)
    return im

def removeBlackPixels(sprite : Image.Image):
    data_in = np.array(sprite)
    data_out = np.array(data_in)
    r1, g1, b1 = (0,0,0)  # Original value
    red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    data_out[:, :, :][mask] = [0,0,0,0]
    
    return Image.fromarray(data_out)


def checkPrimaryColor(sprite : Image.Image, palette : pal.Palette = pal.orct):
    data = np.array(sprite)
    colors = palette[18]
    for color in colors:
        if np.equal(color, data[:,:,:3]).all(axis=2).any():
            return True
        
    return False

def checkSecondaryColor(sprite : Image.Image, palette : pal.Palette = pal.orct):
    data = np.array(sprite)
    colors = palette[16]
    for color in colors:
        if np.equal(color, data[:,:,:3]).all(axis=2).any():
            return True
        
    return False

def checkColor(sprite : Image.Image, color_name : str,  palette : pal.Palette = pal.orct):
    data = np.array(sprite)
    colors = palette[pal.color_dict[color_name]]
    for shade in colors:
        if np.equal(shade, data[:,:,:3]).all(axis=2).any():
            return True
        
    return False


def remapColor(sprite : Image.Image, color_name_old : str, color_name_new : str,  palette : pal.Palette = pal.orct):
    data_in = np.array(sprite)
    data_out = np.array(data_in)
    
    color_old = palette.getColor(color_name_old)
    color_new = palette.getColor(color_name_new)
   
    for i in range(12):
        
        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]
    
 
    return Image.fromarray(data_out)

def colorFirstRemap(sprite : Image.Image, color_name : str,  palette : pal.Palette = pal.orct, remap_colors : pal.Palette = pal.ingame_remaps):
    data_in = np.array(sprite)
    data_out = np.array(data_in)
    
    if color_name == 'NoColor':
        return sprite
        
    color_old = palette.getColor('1st Remap')
    color_new = remap_colors.getColor(color_name)
   
    for i in range(12):
        
        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]
    
 
    return Image.fromarray(data_out)


def colorSecondRemap(sprite : Image.Image, color_name : str,  palette : pal.Palette = pal.orct, remap_colors : pal.Palette = pal.ingame_remaps):
    data_in = np.array(sprite)
    data_out = np.array(data_in)
    
    if color_name == 'NoColor':
        return sprite
    
    color_old = palette.getColor('Pink')
    color_new = remap_colors.getColor(color_name)
   
    for i in range(12):
        
        r1, g1, b1 = color_old[i]  # Original value
        r2, g2, b2 = color_new[i]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]
    
 
    return Image.fromarray(data_out)