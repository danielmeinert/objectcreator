# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 11:39:05 2021

@author: Daniel
"""

import numpy as np
from PIL import Image
import palette as pal


def _decrBr(data_in,color):
    data_out = np.array(data_in)

    for i in range(12):
        j=i
        if(i>0):
            j -=1
        r1, g1, b1 = color[i]  # Original value
        r2, g2, b2 = color[j]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]
            

    return data_out        

def _incrBr(data_in,color):
    data_out = np.array(data_in)

    for i in range(12):
        j=i
        if(i<11):
            j +=1
        r1, g1, b1 = color[i]  # Original value
        r2, g2, b2 = color[j]  # Value that we want to replace it with
        red, green, blue = data_in[:, :, 0], data_in[:, :, 1], data_in[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data_out[:, :, :3][mask] = [r2, g2, b2]
    
    
    return data_out  


# def decreaseBrightness(image, step=1, palette=pal.rct):
#     data = np.array(image)
    
#     for i in range(step):
#         data = decrBr(data,palette)
    
#     return Image.fromarray(data)
    
# def increaseBrightness(image, step=1,palette = pal.rct):
#     data = np.array(image)
    
#     for i in range(step):
#         data = incrBr(data,palette)
    
#     return Image.fromarray(data)   

def _changeBrightnessColor(image : Image.Image, step : int , color : str, palette : pal.Palette=pal.orct):
    """Function to change the brightness of a given image along a given color index of the palette. 
    Input: image;                        PIL image file you want to convert
           step;                         integer number of how many steps you want to change brightness (positive and negative allowed)
           palette (optional);               palette in (20,12,3) shape along which you want to change the brightness. Default: rct_palette
           include_sparkles (optional);  bool value if you want to include water_sparkles color. Including them might cause artifacts/errors because of same colors in the sparkles and watercolor 
    """
    data = np.array(image)
    
    if color not in palette.color_dict.keys():
        return image
    
    color_arr= palette.getColor(color)
    
    if(step < 0):
        for i in range(-step):
            data = _decrBr(data,color_arr)
    else:
        for i in range(step):
            data = _incrBr(data,color_arr)    
    
    return Image.fromarray(data)   
    



def changeBrightness(image : Image.Image, step : int, palette : pal.Palette=pal.orct, include_sparkles = False):
    """Function to change the brightness of a given image along the colorline of the palette. 
    Input: image;                        PIL image file you want to convert
           step;                         integer number of how many steps you want to change brightness (positive and negative allowed)
           palette (optional);               palette in (20,12,3) shape along which you want to change the brightness. Default: rct_palette
           include_sparkles (optional);  bool value if you want to include water_sparkles color. Including them might cause artifacts/errors because of same colors in the sparkles and watercolor 
    """
    
    if include_sparkles and palette.has_sparkles:
        image = _changeBrightnessColor(image, step, 'Sparkles', palette)
    elif include_sparkles:
        raise TypeError('Asked to include sparkles but given palette has no sparkles.')
        
    image = changeBrightnessColor(image, step, list(palette.color_dict.keys()), palette)

    return image      
      
    
def changeBrightnessColor(image : Image.Image, step : int , color, palette : pal.Palette=pal.orct):
    """Function to change the brightness of a given image along a given color index of the palette. 
    Input: image;                        PIL image file you want to convert
           step;                         integer number of how many steps you want to change brightness (positive and negative allowed)
           palette (optional);               palette in (20,12,3) shape along which you want to change the brightness. Default: rct_palette
           include_sparkles (optional);  bool value if you want to include water_sparkles color. Including them might cause artifacts/errors because of same colors in the sparkles and watercolor 
    """
    
    if type(color) == list:
        for color_name in color:
            image = _changeBrightnessColor(image, step, color_name, palette)
    else: 
        image = _changeBrightnessColor(image, step, color, palette)

    return image


    
    
#im.save('sprite_conv.png')


