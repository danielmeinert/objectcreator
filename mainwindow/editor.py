# -*- coding: utf-8 -*-

import rctobject.sprites as spr
import rctobject.objects as obj
import rctobject.palette as pal
import rctobject.constants as cts

class Editor:
    def __init__(self):
        
        self.objects = []
        self.obj_ind = 0 # index of currently open object
        self.new_object_count = 1
        
        self.sprite = []
        self.spr_ind = 0 # index of currently open sprite
        
        
    def newObject(self, obj_type: cts.Type ):
        o = obj.newEmpty(obj_type)
        self.objects.append(o)
        self.obj_ind = self.objects.index(o)
        
        name = f'Object {self.new_object_count}'
        self.new_object_count += 1

        return o, name
    
    def openObjectFile(self, path):
        
        o = obj.load(path)
        
        
        name = o.data['id']
        if not name and o.old_id:
            name = o.old_id
        else:
            name = f'Object {self.new_object_count}'
            self.new_object_count += 1
        
        self.objects.append(o)
        self.obj_ind = self.objects.index(o)
        
        return o, name
    
    
    def closeObject(self, index):
        self.objects.pop(self.obj_ind)
        self.obj_ind = index
        
    
        
    