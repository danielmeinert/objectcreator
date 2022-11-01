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
        
        

    
    
    
    def closeObject(self, index):
        self.objects.pop(self.obj_ind)
        self.obj_ind = index
        
    
        
    