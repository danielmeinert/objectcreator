# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 21:40:31 2022

@author: Daniel
"""

import os
from shutil import unpack_archive, make_archive, move, rmtree

gen_path = 'C:/Users/Daniel/Documents/GitHub/objectmaker/editor_app/pathgenerator'

dirs = next(os.walk(f'{gen_path}/templates_raw'))[1]

for dir in dirs:
    if dir.endswith('wip'):
        continue
    make_archive(base_name=f'{gen_path}/templates/{dir}', root_dir=f'{gen_path}/templates_raw/{dir}', format='zip')
    os.replace(f'{gen_path}/templates/{dir}.zip', f'{gen_path}/templates/{dir}.template')
