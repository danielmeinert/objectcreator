# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 16:53:24 2021

@author: Daniel
"""

import numpy as np
from PIL import Image
import brightness as br
import palette as pal
import generate_surfaces as gen 
import os


root = os.getcwd() + '/sprites'

types = ['grass','sand','ice','sand_red', 'sand_brown', 'dirt', 'rock', 'martian', ]

for top in types:
    for bottom in types:
        if top == bottom:
            continue
        
        gen.generateMixedSurface(top, bottom, root)











