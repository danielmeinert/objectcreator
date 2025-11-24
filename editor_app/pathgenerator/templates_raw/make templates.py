# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 21:40:31 2022

@author: Daniel
"""

import os
from shutil import unpack_archive, make_archive, move, rmtree


dirs = next(os.walk('.'))[1]

for dir in dirs:
    make_archive(base_name=dir, root_dir=dir, format='zip')
    os.replace(f'{dir}.zip', f'../templates/{dir}.template')
    
