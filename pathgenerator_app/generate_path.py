# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 19:57:16 2022

@author: Daniel
"""

from PIL import Image

import rctobject.sprites as spr
import rctobject.objects as obj
import rctobject.palette as pal
import template as templ
from json import load
from os import listdir
from copy import deepcopy


class pathObject:

    def __init__(self, base: Image.Image):
        self.base = base

    def generateObject(self, template: templ.pathTemplate, settings_input: dict):

        data = deepcopy(template.data)
        settings = deepcopy(settings_input)

        data['authors'] = settings['author']
        data['version'] = settings['version']
        data['id'] = settings['author_id'] + '.scenery_large.' + \
            settings['object_id'] + '_' + data['id']

        if settings['hasPrimaryColour']:
            data['properties']['hasPrimaryColour'] = settings['hasPrimaryColour']
        if settings['hasSecondaryColour']:
            data['properties']['hasSecondaryColour'] = settings['hasSecondaryColour']
        data['properties']['cursor'] = settings['cursor']

        if settings['autoNaming']:
            for lang in settings['name']:
                data['strings']['name'][lang] = settings['name'][lang]['pre'] + ' ' + \
                    data['strings']['name'][lang] + ' ' + \
                    settings['name'][lang]['suf']
        else:
            for lang in settings['name']:
                data['strings']['name'][lang] = settings['name'][lang]['pre']

        base = [self.base, self.base, self.base, self.base]

        if settings['autoRotate']:
            base[1] = self.base.transpose(Image.FLIP_LEFT_RIGHT)
            base[2] = (self.base.transpose(Image.FLIP_LEFT_RIGHT)
                       ).transpose(Image.FLIP_TOP_BOTTOM)
            base[3] = self.base.transpose(Image.FLIP_TOP_BOTTOM)

        if template.num_tiles == 1:
            preview_skip = 0
        else:
            preview_skip = 4

        sprites = {}
        rot = 0
        for i, im in enumerate(data['images']):
            if i < preview_skip:
                sprites[im['path']] = spr.Sprite(template.images[im['path']])
                continue

            mask = template.images[im['path']]

            image = spr.pasteOnMask(mask, base[rot].image)

            bbox = image.getbbox()

            if i < 4:
                x = -32 + bbox[0]
                y = 16 + bbox[1]
            else:
                x = -32 + bbox[0]
                y = -8 + bbox[1]

            image = image.crop(bbox)
            sprites[im['path']] = spr.Sprite(image, (x, y))
            rot = (rot + 1) % 4

        self.object = obj.new(data, sprites)

        # Create preview thumbnails for multile objects
        if template.num_tiles > 1:
            self.object.createThumbnails()

    def save(self, filepath: str = None, no_zip: bool = False):
        if self.object:
            self.object.save(filepath, no_zip=no_zip)


class pathGenerator:
    def __init__(self):
        self.loadSettings()
        self.loadTemplatesAtStart()
        self.selected_templates = []
        self.base = spr.Sprite(None)
        self.current_palette = pal.orct
        self.selected_colors = {
            color: False for color in self.current_palette.color_dict}

    def loadSettings(self):
        try:
            self.settings = load(fp=open('config.json'))
        except FileNotFoundError:
            self.settings = {}
            self.settings['author'] = ''
            self.settings['author_id'] = ''
            self.settings['no_zip'] = False

        self.settings['name'] = {'en-GB': {}}
        self.settings['object_id'] = ''
        self.settings['hasPrimaryColour'] = False
        self.settings['hasSecondaryColour'] = False
        self.settings['cursor'] = "CURSOR_PATH_DOWN"
        self.settings['autoNaming'] = False
        self.settings['autoRotate'] = False

    def loadTemplatesAtStart(self):
        self.templates = {}
        for file in listdir("templates"):
            if file.endswith(".template"):
                template = templ.pathTemplate.fromFile(f'templates/{file}')
                if template:
                    self.templates[template.name] = template

    def loadTemplate(self, path: str):
        template = templ.pathTemplate.fromFile(path)

        if template:
            # only add template if not already loaded
            if template.name not in self.templates.keys():
                self.templates[template.name] = template

                return template.name
            else:
                return
        else:
            print('Template file was not type path_tile.')

    def loadBase(self, path: str):
        self.base = spr.Sprite.fromFile(path)

        self.base.crop()
        self.base.x = -int(self.base.image.size[0]/2)
        self.base.y = 0

    def setName(self, prefix: str, suffix: str = ''):
        if self.settings['autoNaming']:
            self.settings['name']['en-GB']['pre'] = prefix
            self.settings['name']['en-GB']['suf'] = suffix
        else:
            self.settings['name']['en-GB']['pre'] = prefix

    def fixBaseToMask(self):
        if self.base.image.size != (1, 1):
            mask = self.templates['Fulltile'].images['images/00.png'].copy()
            image = self.base.image.crop(
                (-32-self.base.x, -self.base.y, -self.base.x+32, -self.base.y+31))
            mask.paste(image, mask)

            self.base = spr.Sprite(mask, (-32,0))


    def generate(self, output_folder: str):

        self.settings['hasPrimaryColour'] = self.base.checkPrimaryColor()
        self.settings['hasSecondaryColour'] = self.base.checkSecondaryColor()

        if self.base.image.size == (1,1):
            return 'No base image loaded!'

        elif self.selected_templates == []:
            return 'No templates selected!'

        elif self.settings['object_id'] == '':
            return 'No object ID given!'

        else:
            self.fixBaseToMask()
            path_obj = pathObject(self.base)
            for name in self.selected_templates:
                template = self.templates[name]
                path_obj.generateObject(template, self.settings)
                path_obj.save(output_folder, self.settings['no_zip'])

            return 'Objects sucessfully created!'

  # def setPreviewImage(self):
   #   pass
   #   pass
