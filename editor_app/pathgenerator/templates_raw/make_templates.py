# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 21:40:31 2022

@author: Daniel
"""

import os
from shutil import unpack_archive, make_archive, move, rmtree


dirs = next(os.walk('C:/Users/Daniel/Documents/GitHub/objectmaker/editor_app/pathgenerator/templates_raw'))[1]

for dir in dirs:
    if dir.endswith('wip'):
        continue
    make_archive(base_name=dir, root_dir=dir, format='zip')
    os.replace(f'{dir}.zip', f'C:/Users/Daniel/Documents/GitHub/objectmaker/editor_app/pathgenerator/templates/{dir}.template')
