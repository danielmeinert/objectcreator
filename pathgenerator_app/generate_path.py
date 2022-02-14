# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 19:57:16 2022

@author: Daniel
"""

from PIL import Image

import sprites as spr
import objects as obj
import template as templ
import palette as pal
from json import load
from os import listdir


class pathObject:
    
    def __init__(self, base: Image.Image):
        self.base = base
        

    def generateObject(self, template: templ.pathTemplate, settings: dict):
        
        data = dict(template.data)
        
        data['authors'] = settings['author']
        data['version'] = settings['version'] 
        data['id'] = settings['author_id'] + '.scenery_large.' + settings['object_id'] + '_' + data['id']
        
        if settings['hasPrimaryColour']:
            data['properties']['hasPrimaryColour'] = settings['hasPrimaryColour']
        if settings['hasSecondaryColour']:
            data['properties']['hasSecondaryColour'] = settings['hasSecondaryColour']
        data['properties']['cursor'] = settings['cursor']
        
        
        if settings['autoNaming']:
            for lang in settings['name']:
                data['strings']['name'][lang] = settings['name'][lang]['pre'] + ' ' + data['strings']['name'][lang] + ' ' + settings['name'][lang]['suf']
        else:
            for lang in settings['name']:
                data['strings']['name'][lang] = settings['name'][lang]['pre']

        
        base= [self.base,self.base,self.base,self.base]
        
        if settings['autoRotate']:
            base[1] = self.base.transpose(Image.FLIP_LEFT_RIGHT)
            base[2] = (self.base.transpose(Image.FLIP_LEFT_RIGHT)).transpose(Image.FLIP_TOP_BOTTOM)
            base[3] = self.base.transpose(Image.FLIP_TOP_BOTTOM)         
            
        if template.num_tiles == 1: 
            preview_skip = 0 
        else:
            preview_skip = 4
        i = 0
        images = {}
        rot = 0
        for im in data['images']:
            if i < preview_skip:
                images[im['path']] = template.images[im['path']]
                i += 1
                continue
            
            mask = template.images[im['path']]
            
            
            sprite = spr.pasteOnMask(mask, base[rot])
            sprite = spr.removeBlackPixels(sprite)
            
            bbox = sprite.getbbox()
            
            if i < 4:
                im['x'] = -32 + bbox[0]
                im['y'] = 16 + bbox[1]
            else:    
                im['x'] = -32 + bbox[0]
                im['y'] = -8 + bbox[1]
            
            sprite = sprite.crop(bbox)
            images[im['path']] = sprite
            rot = (rot + 1) % 4
            
            i += 1
        
        self.object = obj.RCTObject(data, images)
        
        #Create preview thumbnails for multile objects
        if template.num_tiles >1:
            for rot in range(4):
                im = self.object.data['images'][rot]
                sprite = self.object.showSprite()
                sprite.thumbnail((64,112))
                sprite = pal.addPalette(sprite)
                sprite = spr.removeBlackPixels(sprite)
                im['x'] = -32
                im['y'] = 16
                self.object.images[im['path']] = sprite
                self.object.rotateObject()
        
            self.object.rotateObject()

        
                
        
    def save(self, filepath : str = None, no_zip : bool = False):
        if self.object:
            self.object.save(filepath, no_zip)
        
class pathGenerator:
    def __init__(self):
        self.loadSettings()
        self.loadTemplatesAtStart()
        self.selected_templates = []
        self.base = None
        
        
    def loadSettings(self):
        try:
            self.settings = load(fp=open('config.json'))
        except:
            self.settings = {}
            self.settings['author'] = ''
            self.settings['author_id'] = ''
            self.settings['no_zip'] = False

            
        
        self.settings['name'] = {'en-GB':{}}
        self.settings['object_id'] = ''
        self.settings['hasPrimaryColour'] =  False
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
                    
                
    def loadTemplate(self, path : str):
        template = templ.pathTemplate.fromFile(path)
        
        if template:
            #only add template if not already loaded
            if template.name not in self.templates.keys():
                self.templates[template.name] = template
            
                return template.name
            else:
                return
        else:
            print('Template file was not type path_tile.')
        
        
    def loadBase(self, path : str):
        self.base_raw = Image.open(path).convert('RGBA')
        
        self.base_raw = spr.removeBlackPixels(self.base_raw)
        
        self.settings['hasPrimaryColour'] = spr.checkPrimaryColor(self.base_raw)
        self.settings['hasSecondaryColour'] = spr.checkSecondaryColor(self.base_raw)
        
        self.base_raw = self.base_raw.crop(self.base_raw.getbbox())
        self.base = self.base_raw.crop((0,0,64,31))
        
        canvas = Image.new('RGBA', (172,132))
        canvas.paste(self.base,(86-int(self.base.size[0]/2),66-int(self.base.size[1]/2)),self.base)
        
        self.preview = canvas
        
    
    def setName(self,prefix : str, suffix : str = ''):
        if self.settings['autoNaming']:
            self.settings['name']['en-GB']['pre'] = prefix
            self.settings['name']['en-GB']['suf'] = suffix
        else:
            self.settings['name']['en-GB']['pre'] = prefix
        
    def generate(self, output_folder : str):
                
        if self.base == None:
            return 'No base image loaded!'
        
        elif self.selected_templates == []:
            return 'No templates selected!'
        
        elif self.settings['object_id'] == '':
            return 'No object ID given!'
        
        else:
            obj = pathObject(self.base)

            for name in self.selected_templates:
                template = self.templates[name]
                obj.generateObject(template, self.settings)
                obj.save(output_folder, self.settings['no_zip'])
            
            return 'Objects sucessfully created!'
       

        
     
        
  
        
  
    
  
    
  
    
  #def setPreviewImage(self):
   #   pass
        
                
    
        

    
    
    
    