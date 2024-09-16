# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2024 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from json import load, dump
from os import mkdir, replace, walk
from PIL import Image
from shutil import unpack_archive, make_archive
from tempfile import TemporaryDirectory


class PathTemplate:

    def __init__(self, data: dict, images: dict, is_small: bool):
        """Instantiate object directly given JSON and image data."""
        self.data = data
        self.images = images
        self.is_small = is_small
        self.name = data['strings']['name']['en-GB']

    @classmethod
    def fromFile(cls, path: str):
        """Instantiates a new object from a .template file."""
        with TemporaryDirectory() as temp:
            unpack_archive(filename=path, extract_dir=temp, format='zip')
            # Raises error on incorrect object structure or missing json:
            try:
                data_raw = load(fp=open(f'{temp}/object.json'))
            except:
                print(
                    f'Warning: template file {path} corrupted. Skipped loading.')
                return

            if not (data_raw["template_type"] == "path_tile" or data_raw["template_type"] == "path_tile_small"):
                return

            is_small = (data_raw["template_type"] == "path_tile_small")

            data = data_raw['json']

            preview_skip = 0 if is_small else 4
            i = 0
            images = {}
            for path in next(walk(f'{temp}/images'))[2]:
                if i < preview_skip:
                    images[f'images/{path}'] = Image.new('RGBA', (1, 1))
                    i += 1
                    continue

                images[f'images/{path}'] = Image.open(
                    f'{temp}/images/{path}').convert('RGBA')

        return cls(data=data, images=images, is_small=is_small)

    def save(self, path: str):
        """Saves an object as .parkobj file to specified path."""
        with TemporaryDirectory() as temp:
            with open(f'{temp}/object.json', mode='w') as file:
                dump(obj=self.data, fp=file, indent=2)
            mkdir(f'{temp}/images')
            for name, image in self.images.items():
                image.save(f'{temp}/{name}')
            filename = path + '/' + self.data['id']
            make_archive(base_name=f'{filename}', root_dir=temp, format='zip')
            replace(f'{filename}.zip', f'{filename}.template')
