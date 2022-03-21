# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 13:23:22 2021

@author: Daniel
"""

import os
from PIL import Image, ImageOps
from shutil import make_archive, copyfile
from json import load, dump

import palette as pal
import sprites as spr

types = ['grass','sand','ice','sand_red', 'sand_brown', 'dirt', 'rock', 'martian', ]

names = {'grass' : 'Grass','sand' : 'Sand', 'ice': 'Ice ','sand_red' : 'Sand (Red)', 'sand_brown' : 'Sand (Brown)', 'dirt' : 'Dirt', 'rock' : 'Rock', 'martian' : 'Martian'}


def generateMixedSurface(top_name, bottom_name, folder):
    
    root = folder
    
    data = load(fp=open(f'{root}/object.json'))
       
    
    top_folder = root + '/' + top_name
    bottom_folder = root + '/' + bottom_name
    mask_folder = root + '/masks'
    
    merge_folder =  root + '/' + bottom_name + '_' + top_name
    
    os.makedirs(f'{merge_folder}/images',exist_ok=True)
    
    ID= "tols.terrain_surface." + bottom_name + '_' + top_name
    data['id'] = ID
    
    for lang in data['strings']['name']:
        data['strings']['name'][lang] = names[bottom_name] + '/' + names[top_name] + ' mixed' 
    
    for im in data['images']:
        im_name = im['path'].replace('images/', '')
                
        top = Image.open(f'{top_folder}/{im_name}').convert('RGBA')
        bottom = Image.open(f'{bottom_folder}/{im_name}').convert('RGBA')
        mask = Image.open(f'{mask_folder}/{im_name}').convert('RGBA')
        
        top = spr.pasteOnMask(mask, top)
        fin = spr.mergeSprites(top, bottom, palette= pal.save_colors)
        
        fin.save(f'{merge_folder}/images/{im_name}')
     
    with open(f'{merge_folder}/object.json', mode='w') as file:
        dump(data, fp=file,indent=2)
        
    make_archive(base_name=f'{root}/objects/{ID}', root_dir=merge_folder, format='zip')
    os.replace(f'{root}/objects/{ID}.zip', f'{root}/objects/{ID}.parkobj')
    return 
    
    
def generateMaskSprites(folder_in, folder_out):
    
        
    base = {
        "flat": Image.open(f'{folder_in}/flat.png'),
        "right_up": Image.open(f'{folder_in}/right_up.png').convert('RGBA'),
        "right_down": Image.open(f'{folder_in}/right_down.png').convert('RGBA'),
        "down": Image.open(f'{folder_in}/down.png').convert('RGBA'),
        "right": Image.open(f'{folder_in}/right.png').convert('RGBA')
        }
    
    
    
    #0
    im = base["flat"]
    im.save(f'{folder_out}/00.png')
    
    #1
    im_l = base["right"].crop(box=(0, 0,32,base["right"].height))
    im_l = ImageOps.expand(im_l, border=(0, 0,32,0), fill = (0,0,0,0))
    im_r = base["flat"].crop(box=(32, 0,64,base["flat"].height))
    im_r = ImageOps.expand(im_r, border=(32, 1,0,0), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    im.save(f'{folder_out}/01.png')
    
    #2
    im = base["flat"].crop(box=(0, 0,64,16))
    im.save(f'{folder_out}/02.png')
    
    #3
    im = base["right_up"]
    im.save(f'{folder_out}/03.png')
    
    #4
    im_l = base["flat"].crop(box=(0, 0,32,base["flat"].height))
    im_l = ImageOps.expand(im_l, border=(0, 1,32,0), fill = (0,0,0,0))
    im_r = (base["right"].transpose(Image.FLIP_TOP_BOTTOM)).crop(box=(32, 0,64,32))
    im_r = ImageOps.expand(im_r, border=(32, 0,0,0), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    
    im.save(f'{folder_out}/04.png')
    
    #5
    im_l = base["right"].crop(box=(0, 0,32,base["right"].height))
    im_l = ImageOps.expand(im_l, border=(0, 0,32,0), fill = (0,0,0,0))
    im_r = base["right"].crop(box=(32, 0,64,base["right"].height)).transpose(Image.FLIP_TOP_BOTTOM)
    im_r = ImageOps.expand(im_r, border=(32, 0,0,0), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    im.save(f'{folder_out}/05.png')  
    
    #6
    im = base["right_up"].transpose(Image.FLIP_TOP_BOTTOM)
    im.save(f'{folder_out}/06.png')
    
    #7
    im = base["flat"].crop(box=(0, 16,64,32))
    im.save(f'{folder_out}/07.png')
     
    #8
    im_l = base["down"].crop(box=(0, 0,64,31))
    im_l = ImageOps.expand(im_l, border=(0, 0,0,16), fill = (0,0,0,0))
    im_r = base["flat"].crop(box=(0, 16,64,32))
    im_r = ImageOps.expand(im_r, border=(0, 31,0,0), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    im.save(f'{folder_out}/08.png')
    
    #9
    im = base["right_down"]
    im.save(f'{folder_out}/09.png')  
    
    #10
    im = base["down"].crop(box=(0, 0,64,32))
    im.save(f'{folder_out}/10.png')  
    
    #11
    im_l = base["flat"].crop(box=(0, 0,32,base["flat"].height))
    im_l = ImageOps.expand(im_l, border=(0, 0,31,0), fill = (0,0,0,0))
    im_r = base["right"].crop(box=(33, 1,64,32))
    im_r = ImageOps.expand(im_r, border=(32, 0,0,0), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    im.save(f'{folder_out}/11.png')
    
    #12
    im = base["right_down"].transpose(Image.FLIP_TOP_BOTTOM)
    im.save(f'{folder_out}/12.png')  
    
    #13
    im_l = base["down"].crop(box=(0, 33,64,64))
    im_l = ImageOps.expand(im_l, border=(0, 16,0,0), fill = (0,0,0,0))
    im_r = base["flat"].crop(box=(0, 0,64,16))
    im_r = ImageOps.expand(im_r, border=(0, 0,0,31), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    im.save(f'{folder_out}/13.png')
    
    #14
    im_l = (base["right"].transpose(Image.FLIP_TOP_BOTTOM)).crop(box=(0, 0,31,31))
    im_l = ImageOps.expand(im_l, border=(0, 0,32,0), fill = (0,0,0,0))
    im_r = base["flat"].crop(box=(32, 0,64,31))
    im_r = ImageOps.expand(im_r, border=(31, 0,0,0), fill = (0,0,0,0))
    
    im = Image.alpha_composite(im_l, im_r)
    
    im.save(f'{folder_out}/14.png')
    
    #15
    im = base["down"]
    im.save(f'{folder_out}/15.png')  
    
    #16
    im = Image.new('RGBA', (1,1))
    im.save(f'{folder_out}/16.png')  
    
    #17
    im = base["right"]
    im.save(f'{folder_out}/17.png')  
    
    #18
    im = base["right"].transpose(Image.FLIP_TOP_BOTTOM)
    im.save(f'{folder_out}/18.png')  
    
    for i in range(19):
        num_in = str(i).zfill(2)
        num_out1 = str(i+19).zfill(2)
        num_out2 = str(i+38).zfill(2)
        copyfile(f'{folder_out}/{num_in}.png',f'{folder_out}/{num_out1}.png')
        copyfile(f'{folder_out}/{num_in}.png',f'{folder_out}/{num_out2}.png')

    return
     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    