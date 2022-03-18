"""
Module for handling base classes of RCT objects.
Includes file handling (save/open) functions.

Objects may be loaded with from_parkobj and from_dat functions.

JSON data may be accessed and edited as dictionary key: obj[key]

TODO: Loading object from .DAT files

Created 09/26/2021; 16:58:33
@author: Drew
"""

from json import load, dump, loads
from os import mkdir, replace
from PIL import Image
from shutil import unpack_archive, make_archive, move, rmtree
from tempfile import TemporaryDirectory
from subprocess import run
import numpy as np
from numpy.linalg import matrix_power
import rctobject.sprites as spr
import rctobject.datloader as dat

OPENRCTPATH = 'C:\\Users\\puvlh\\Documents\\OpenRCT2\\bin'


class RCTObject:
    """Base class for all editable objects; loads from .parkobj or .DAT files."""

    def __init__(self, data: dict, sprites: dict):
        """Instantiate object directly given JSON and image data."""
        self.data = data
        self.sprites = sprites
        self.rotation = 0
        if data:
            self.tile_size = self.setTileSize()
        self.current_first_remap = 'NoColor'
        self.current_second_remap = 'NoColor'

    def __getitem__(self, item: str):
        """Returns value of given item from the object's JSON data."""
        return self.data[item]

    def __setitem__(self, item: str, value: str or dict):
        """Adds/changes a value of given item in object's JSON data."""
        self.data[item] = value

    @classmethod
    def fromParkobj(cls, path: str):
        """Instantiates a new object from a .parkobj file."""
        with TemporaryDirectory() as temp:
            unpack_archive(filename=path, extract_dir=temp, format='zip')
            # Raises error on incorrect object structure or missing json:
            data = load(fp=open(f'{temp}/object.json'))
            sprites = {im['path']: spr.sprite.fromFile(
                f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}

        return cls(data=data, sprites=sprites)

    @classmethod
    def from_dat(cls, path: str):
        """TODO: Instantiates a new object from a .DAT file."""

        data = dat.read_dat_info(path)
        dat_id = data['originalId'].split('|')[1].replace(' ', '')
        with TemporaryDirectory() as temp:
            result = run([f'{OPENRCTPATH}/openrct2', 'sprite',
                         'exportalldat', dat_id, f'{temp}/images'], stdout=-1, encoding='utf-8')
            string = result.stdout
            string = string[string.find('{'):].replace(f'{temp}/', '')
            string = string.replace('\\', '/')
            i = -1
            while string[i] != ',':
                i -= 1

            data['images'] = loads(f'[{string[:i]}]', encoding='utf-8')

            sprites = {im['path']: spr.sprite.fromFile(
                f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}

        return cls(data=data, sprites=sprites)

    def save(self, path: str, name: str = None, include_originalId: bool = False, no_zip: bool = False):
        """Saves an object as .parkobj file to specified path."""

        # Bring object in default rotation
        self.rotateObject(-self.rotation)
        self.updateImageOffsets()

        if not include_originalId:
            self.data.pop('originalId')

        if name:
            filename = path + '/' + name
        else:
            filename = path + '/' + self.data['id']

        with TemporaryDirectory() as temp:
            mkdir(f'{temp}/images')
            with open(f'{temp}/object.json', mode='w') as file:
                dump(obj=self.data, fp=file, indent=2)
            for name, sprite in self.sprites.items():
                sprite.save(f'{temp}/{name}')
            make_archive(base_name=f'{filename}',
                         root_dir=temp, format='zip')

            replace(f'{filename}.zip', f'{filename}.parkobj')
            if no_zip:
                rmtree(filename, ignore_errors=True)
                mkdir(filename)
               # mkdir(f'{filename}/images')
                move(f'{temp}/images', filename)
                move(f'{temp}/object.json', filename)

    def numTiles(self):
        if self.data['objectType'] != 'scenery_large':
            return 1
        else:
            return len(self.data['properties']['tiles'])

    def setTileSize(self):
        if self.data['objectType'] != 'scenery_large':
            return (1, 1, int(self.data['properties']['height']/8))

        max_x = 0
        max_y = 0
        max_z = 0
        for tile in self.data['properties']['tiles']:
            max_x = max(tile['x'], max_x)
            max_y = max(tile['y'], max_y)
            max_z = max(tile.get('z', 0) + tile['clearance'], max_z)

        x = (max_x + 32)/32
        y = (max_y + 32)/32
        z = max_z / 8

        return (int(x), int(y), int(z))

    def spriteBoundingBox(self, view: int = None):
        if view is None:
            view = self.rotation

        if self.data['objectType'] != 'scenery_large':
            return list(self.sprites.values())[view].image.size()

        x, y, z = self.tile_size

        height = -1 + x*16 + y*16 + z*8
        width = x*32 + y*32

        return (width, height)

    def updateImageOffsets(self):

        for im in self.data['images']:
            im['x'] = self.sprites[im['path']].x
            im['y'] = self.sprites[im['path']].y

    def showSprite(self):
        if self.numTiles() == 1:
            return self.sprites[list(self.sprites)[self.rotation]].show(self.current_first_remap, self.current_second_remap)

        x_size, y_size, z_size = self.tile_size
        canvas = Image.new('RGBA', self.spriteBoundingBox())

        tiles = self.data['properties']['tiles']
        tile_index = 0

        view = self.rotation

        drawing_order = self.getDrawingOrder()

        # Set base point of (0,0) tile according to rotation
        if view == 0:
            y_baseline = z_size*8
            x_baseline = x_size*32
        elif view == 1:
            y_baseline = z_size*8+(x_size-1)*16
            x_baseline = x_size*32+(y_size-1)*32
        elif view == 2:
            y_baseline = z_size*8+(x_size-1)*16+(y_size-1)*16
            x_baseline = y_size*32
        elif view == 3:
            y_baseline = z_size*8+(y_size-1)*16
            x_baseline = 32
        else:
            raise ValueError('view index out of range')

        for tile_index in drawing_order:
            tile = tiles[tile_index]
            y_base = y_baseline + int(tile['x']/2) + int(tile['y']/2)
            x_base = x_baseline - tile['x'] + tile['y']

            sprite_index = 4 + 4*tile_index+view
            sprite = self.sprites[self.data['images'][sprite_index]['path']]
            canvas.paste(sprite.show(self.current_first_remap, self.current_second_remap),
                         (x_base+sprite.x, y_base+sprite.y), sprite.image)

        return canvas.crop(canvas.getbbox())

    def rotateObject(self, rot: int = 1):
        self.rotation = (self.rotation + rot) % 4
        if self.numTiles() == 1:
            return

        rot_mat = matrix_power(np.array([[0, 1], [-1, 0]]), rot % 4)

        for tile in self.data['properties']['tiles']:
            pos = np.array([tile['x'], tile['y']])

            pos = rot_mat.dot(pos)
            tile['x'], tile['y'] = int(pos[0]), int(pos[1])

    def getDrawingOrder(self):

        order = {}

        for tile_index, tile in enumerate(self.data['properties']['tiles']):
            score = tile['x'] + tile['y']
            order[tile_index] = score

        return sorted(order, key=order.get)

    def createThumbnails(self):
        if self.data['objectType'] != 'scenery_large':
            return

        for rot in range(4):
            im = self.data['images'][rot]
            image = self.showSprite()
            image.thumbnail((64, 112), Image.NEAREST)
            x = -int(image.size[0]/2)
            y = image.size[1]
            self.sprites[im['path']] = spr.sprite(image, (x, y))
            self.rotateObject()
