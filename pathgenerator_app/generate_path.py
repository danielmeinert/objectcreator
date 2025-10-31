# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from PIL import Image

import rctobject.sprites as spr
import rctobject.objects as obj
import rctobject.palette as pal
import template as templ
from json import load
from os import listdir
from copy import deepcopy


class PathObject:

    def __init__(self, bases: list):
        self.bases = bases

    def generateObject(self, template: templ.PathTemplate, settings_input: dict):

        data = deepcopy(template.data)
        settings = deepcopy(settings_input)

        data['authors'] = settings['author']
        data['version'] = settings['version']

        data['id'] = f"{settings['author_id']}.{data['objectType']}.{settings['object_id']}_{data['id']}"

        if settings['hasPrimaryColour']:
            data['properties']['hasPrimaryColour'] = settings['hasPrimaryColour']
        if settings['hasSecondaryColour']:
            data['properties']['hasSecondaryColour'] = settings['hasSecondaryColour']
        if settings['hasTertiaryColour']:
            data['properties']['hasTertiaryColour'] = settings['hasTertiaryColour']

        data['properties']['cursor'] = settings['cursor']

        if settings['autoNaming']:
            for lang in settings['name']:
                data['strings']['name'][lang] = settings['name'][lang]['pre'] + ' ' + \
                    data['strings']['name'][lang] + ' ' + \
                    settings['name'][lang]['suf']
        else:
            for lang in settings['name']:
                data['strings']['name'][lang] = settings['name'][lang]['pre']

        # 0 = no rotation, 1 = rotation
        if settings['rotationMode'] == 0:
            base = [self.bases[0], self.bases[0], self.bases[0], self.bases[0]]
        else:
            base = [self.bases[0], self.bases[1], self.bases[2], self.bases[3]]

        if template.is_small:
            preview_skip = 0
            num_images = 4
        else:
            preview_skip = 4
            num_images = 4*len(data['properties']['tiles'])+4

        sprites = {}
        images = []
        rot = 0

        for i in range(num_images):
            path = f'images/{i}.png'
            if i < preview_skip:
                sprites[path] = spr.Sprite(None)
                images.append({'path': path, 'x': 0, 'y': 0})
                continue

            mask = template.images[path]

            image = spr.pasteOnMask(mask, base[rot].image)
            sprite = spr.Sprite(image)

            sprite.y -= 8 if settings['raised'] else 0
#            sprite.y += 15 if not template.is_small else 0

            sprites[path] = sprite
            images.append({'path': path, 'x': 0, 'y': 0})

            rot = (rot + 1) % 4

        data['images'] = images
        self.object = obj.new(data, sprites)

        # Create preview thumbnails for LS objects
        if not template.is_small:
            self.object.createThumbnails()

    def save(self, filepath: str = None, no_zip: bool = False):
        if self.object:
            self.object.save(filepath, no_zip=no_zip)


class PathGenerator:
    def __init__(self, fix_mask):
        self.loadSettings()
        self.loadTemplatesAtStart()
        self.selected_templates = []
        self.bases = [spr.Sprite(None), spr.Sprite(
            None), spr.Sprite(None), spr.Sprite(None)]
        self.base = self.bases[0]
        self.current_rotation = 0

        self.current_palette = pal.orct
        self.selected_colors = {
            color: False for color in self.current_palette.color_dict}

        self.fix_mask = fix_mask

    def loadSettings(self):
        try:
            self.settings = load(fp=open('config.json'))
        except FileNotFoundError:
            self.settings = {}
            self.settings['author'] = ''
            self.settings['author_id'] = ''
            self.settings['no_zip'] = False
            self.settings['version'] = '1.0'

        self.settings['name'] = {'en-GB': {}}
        self.settings['object_id'] = ''
        self.settings['hasPrimaryColour'] = False
        self.settings['hasSecondaryColour'] = False
        self.settings['hasTertiarySecondaryColour'] = False
        self.settings['cursor'] = "CURSOR_PATH_DOWN"
        self.settings['autoNaming'] = False
        self.settings['rotationMode'] = 0

    def loadTemplatesAtStart(self):
        self.templates = {}
        for file in listdir("templates"):
            if file.endswith(".template"):
                template = templ.PathTemplate.fromFile(f'templates/{file}')
                if template:
                    self.templates[template.name] = template

    def loadTemplate(self, path: str):
        template = templ.PathTemplate.fromFile(path)

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
        sprite = spr.Sprite.fromFile(path)

        sprite.crop()
        sprite.x = -int(sprite.image.size[0]/2)
        sprite.y = 0

        self.bases[self.current_rotation] = sprite
        self.base = self.bases[self.current_rotation]

    def importBases(self, bases):
        for i, base in enumerate(bases):
            self.bases[i] = spr.Sprite(base, (-32, 0))

    def resetAllBases(self):
        self.bases = [spr.Sprite(None), spr.Sprite(
            None), spr.Sprite(None), spr.Sprite(None)]
        self.base = self.bases[0]
        self.current_rotation = 0

    def setName(self, prefix: str, suffix: str = ''):
        if self.settings['autoNaming']:
            self.settings['name']['en-GB']['pre'] = prefix
            self.settings['name']['en-GB']['suf'] = suffix
        else:
            self.settings['name']['en-GB']['pre'] = prefix

    def fixBaseToMask(self):
        if self.base.image.size != (1, 1):
            mask = self.fix_mask.copy()
            image = self.base.image.crop(
                (-32-self.base.x, -self.base.y, -self.base.x+32, -self.base.y+31))
            mask.paste(image, mask)

            self.bases[self.current_rotation] = spr.Sprite(mask, (-32, 0))
            self.base = self.bases[self.current_rotation]

    def rotationOptionChanged(self, item):
        if not self.settings['rotationMode'] == item:
            self.settings['rotationMode'] = item
            if item == 0:
                self.base = self.bases[0]
                self.current_rotation = 0

    def rotationChanged(self, rot):

        self.current_rotation = rot
        self.base = self.bases[self.current_rotation]

    def generateRotations(self, direction):

        sprite = self.bases[0].image
        x = self.bases[0].x
        y = self.bases[0].y

        if direction == 0:
            self.bases[1] = spr.Sprite(
                sprite.transpose(Image.FLIP_LEFT_RIGHT), (x, y))
            self.bases[2] = spr.Sprite((sprite.transpose(Image.FLIP_LEFT_RIGHT)
                                        ).transpose(Image.FLIP_TOP_BOTTOM), (x, y))
            self.bases[3] = spr.Sprite(
                sprite.transpose(Image.FLIP_TOP_BOTTOM), (x, y))
        elif direction == 1:
            self.bases[1] = spr.Sprite(
                sprite.transpose(Image.FLIP_TOP_BOTTOM), (x, y))
            self.bases[2] = spr.Sprite((sprite.transpose(Image.FLIP_TOP_BOTTOM)
                                        ).transpose(Image.FLIP_LEFT_RIGHT), (x, y))
            self.bases[3] = spr.Sprite(
                sprite.transpose(Image.FLIP_LEFT_RIGHT), (x, y))

        self.base = self.bases[self.current_rotation]

    def generate(self, output_folder: str):

        primary_check = False
        secondary_check = False
        tertiary_check = False

        for base in self.bases:
            if base.image.size == (1, 1):
                return 'Not all base images loaded!'

            primary_check = (base.checkPrimaryColor() or primary_check)
            secondary_check = (base.checkSecondaryColor() or secondary_check)
            tertiary_check = (base.checkTertiaryColor() or tertiary_check)

            if self.settings['rotationMode'] == 0:
                break

        self.settings['hasPrimaryColour'] = primary_check
        self.settings['hasSecondaryColour'] = secondary_check
        self.settings['hasTertiaryColour'] = tertiary_check

        if self.selected_templates == []:
            return 'No templates selected!'

        elif self.settings['object_id'] == '':
            return 'No object ID given!'

        else:
            self.fixBaseToMask()
            path_obj = PathObject(self.bases)
            for name in self.selected_templates:
                template = self.templates[name]
                path_obj.generateObject(template, self.settings)
                path_obj.save(output_folder, self.settings['no_zip'])

            return 'Objects sucessfully created!'

  # def setPreviewImage(self):
   #   pass
   #   pass
