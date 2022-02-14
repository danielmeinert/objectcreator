# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 23:22:04 2022

@author: Daniel
"""

import os
from PIL import Image, ImageOps
from shutil import make_archive, copyfile
from json import load, dump

import palette as pal
import sprites as spr
import objects as obj
import generate_path as gn
import template as tem


settings = {}
settings['author_id'] = 'tols'
settings['object_id'] = 'test'
settings['authors'] = 'Tolsimir'
settings['version'] = '1.0'
settings['hasPrimaryColour'] =  False
settings['hasSecondaryColour'] = False
settings['cursor'] = "CURSOR_PATH_DOWN"

settings['auto_name'] = True
settings['auto_rotate'] = True
settings['name'] = {"en-GB": {'pre': 'Fine Tiled Path', 'post':'by Tolsimir'}}

o = obj.RCTObject.fromParkobj('path_generator/tols.lndwll06.parkobj')
o.showSprite(2)

# input_sprite = Image.open('C:/Users/Daniel/Documents/object_maker/path_generator/00.png').convert('RGBA')

# path = gn.pathObject(input_sprite)
# template = tem.pathTemplate.fromFile(r'C:\Users\Daniel\Documents\object_maker\path_generator\templates\diagonal.template')

# path.generateObject(template, settings)
# data = path.object

#for name, image in data.images.items():
#    image.show()

#folder = 'C:/Users/Daniel/Documents/object_maker/path_generator/'

#gn.generatePath_fulltile(input_sprite,settings,folder)



