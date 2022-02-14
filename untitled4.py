# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 16:41:33 2021

@author: Daniel
"""

import numpy as np
from PIL import Image
import brightness as br
import palette as pal
import sprites as spr

#top = Image.open('top.png')
#top = top.convert('RGB')

left = Image.open('left.png')
left = left.convert('RGBA')

right = Image.open('05.png')
right = right.convert('RGBA')

#top = br.decreaseBrightness(top,0)
#left = br.changeBrightness(left, -1,pal.old_objm)
#right = br.changeBrightness(right,0,pal.old_objm)


a = spr.sprite(right)
a.changeBrightness(1)

# img=left
# width, height = img.size
# m = 1.5
# xshift = abs(m) * width
# new_height = height + int(round(xshift))
# img = img.transform((width, new_height), Image.AFFINE,
#         (1, 0,0,m,1, -xshift if m>0 else 0), Image.NEAREST)
