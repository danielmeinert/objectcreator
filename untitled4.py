# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 16:41:33 2021

@author: Daniel
"""

import numpy as np
from PIL import Image
import rctobject.palette as pal
import rctobject.sprites as spr
import rctobject.objects as obj

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
# a.changeBrightness(1)
b = obj.RCTObject.fromParkobj('X97.CMC2O.zip')
b.createThumbnails()

#b.save('save', 'X97.scenery_large.CMC2O', no_zip = True)

# img=left
# width, height = img.size
# m = 1.5
# xshift = abs(m) * width
# new_height = height + int(round(xshift))
# img = img.transform((width, new_height), Image.AFFINE,
#         (1, 0,0,m,1, -xshift if m>0 else 0), Image.NEAREST)

# data = np.array(pal.rct)
# lookup= np.zeros((32,12,2))

# for j in range(32):
#     color = pal.ingame_remaps[j]
#     for i in range(12):
#         r1, g1, b1 = color[i]  # Original value
#         red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
#         mask = (red == r1) & (green == g1) & (blue == b1)
#         indices = np.where(mask)
#         lookup[j][i] = (indices[0][0],indices[1][0])
