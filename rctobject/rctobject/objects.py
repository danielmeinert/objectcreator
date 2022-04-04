"""
Module for handling base classes of RCT objects.
Includes file handling (save/open) functions.

Objects may be loaded with from_parkobj and from_dat functions.

JSON data may be accessed and edited as dictionary key: obj[key]


Created 09/26/2021; 16:58:33
@author: Tolsimir, Drew
"""

from json import dump, loads
from json import load as jload
from os import mkdir, replace, getcwd
from os.path import splitext
from PIL import Image
from shutil import unpack_archive, make_archive, move, rmtree
from tempfile import TemporaryDirectory
from subprocess import run
import numpy as np
from numpy.linalg import matrix_power
from enum import Enum

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

        self.size = (0, 0, 0)  # to be set in subclass
        self.current_first_remap = 'NoColor'
        self.current_second_remap = 'NoColor'
        self.current_third_remap = 'NoColor'

    def __getitem__(self, item: str):
        """Returns value of given item from the object's JSON data."""
        return self.data[item]

    def __setitem__(self, item: str, value: str or dict or list):
        """Adds/changes a value of given item in object's JSON data."""
        self.data[item] = value

    @classmethod
    def fromParkobj(cls, filepath: str):
        """Instantiates a new object from a .parkobj file."""
        with TemporaryDirectory() as temp:
            unpack_archive(filename=filepath, extract_dir=temp, format='zip')
            # Raises error on incorrect object structure or missing json:
            data = jload(fp=open(f'{temp}/object.json', encoding='utf-8'))
            sprites = {im['path']: spr.Sprite.fromFile(
                f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}

        return cls(data=data, sprites=sprites)
    
    @classmethod
    def fromJson(cls, filepath: str, openpath: str = OPENRCTPATH):
        """Instantiates a new object from a .json file. Sprite exporting is done 
        by openRCT, hence openpath has to be according to the system's openrct2.exe location."""
        data = jload(fp=open(filepath, encoding='utf8'))
        dat_id = data.get('originalId',False)
        # If an original Id was given we load the sprites from original DATs (aka "official" openRCT objects).
        if isinstance(data['images'][0], str) and dat_id:
            dat_id = dat_id.split('|')[1].replace(' ', '')
            with TemporaryDirectory() as temp:
                temp = temp.replace('\\', '/')
                result = run([f'{openpath}/openrct2', 'sprite',
                             'exportalldat', dat_id, f'{temp}/images'], stdout=-1, encoding='utf-8')
                string = result.stdout
                string = string[string.find('{'):].replace(f'{temp}/', '')
                i = -1
                while string[i] != ',':
                    i -= 1
                
                data['images'] = loads(f'[{string[:i]}]', encoding='utf-8')
                sprites = {im['path']: spr.Sprite.fromFile(
                    f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}
        # If no original dat is given, the images are assumed to lie in the relative path given in the json (unzipped parkobj).
        # The file is assumed to be called "object.json" in this case.
        elif isinstance(data['images'][0], dict):
            filename_len = len(filepath.split('/')[-1])
            sprites = {im['path']: spr.Sprite.fromFile(
                f'{filepath[:-filename_len]}{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}
        else:
            raise RuntimeError('Cannot extract images.')

        return cls(data=data, sprites=sprites)
    
    @classmethod
    def fromDat(cls, filepath: str, openpath: str = OPENRCTPATH):
        """Instantiates a new object from a .DAT file. Sprite exporting is done 
        by openRCT, hence openpath has to be according to the system's openrct2.exe location."""

        data = dat.read_dat_info(filepath)
        dat_id = data['originalId'].split('|')[1].replace(' ', '')
        with TemporaryDirectory() as temp:
            temp = temp.replace('\\', '/')
            result = run([f'{openpath}/openrct2', 'sprite',
                         'exportalldat', dat_id, f'{temp}/images'], stdout=-1, encoding='utf-8')
            string = result.stdout
            string = string[string.find('{'):].replace(f'{temp}/', '')
            i = -1
            while string[i] != ',':
                i -= 1

            data['images'] = loads(f'[{string[:i]}]', encoding='utf-8')
            sprites = {im['path']: spr.Sprite.fromFile(
                f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}

        return cls(data=data, sprites=sprites)

    def save(self, path: str = None, name: str = None, no_zip: bool = False, include_originalId: bool = False):
        """Saves an object as .parkobj file to specified path."""
        if not path:
            path = getcwd()
        
        if not self.data.get('id', False):
            raise RuntimeError('Forbidden to save object without id!')
        
        # Reset object to default rotation
        self.rotateObject(-self.rotation)
        
        # If sprites have changed, they have to be updated
        self.updateSpritesList()
        self.updateImageOffsets()

        if not include_originalId and self.data.get('originalId', False):
            self.data.pop('originalId')
            
        if name:
            filename = f'{path}/{name}'
        else:
            filename = f'{path}/{self.data["id"]}'

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
                move(f'{temp}/{name}.json', filename)

    def spriteBoundingBox(self, view: int = None):
        if view is None:
            view = self.rotation

        x, y, z = self.size

        height = -1 + x*16 + y*16 + z*8
        width = x*32 + y*32

        return (width, height)

    def updateImageOffsets(self):
        for im in self.data['images']:
            im['x'] = self.sprites[im['path']].x
            im['y'] = self.sprites[im['path']].y
            
    def updateSpritesList(self):
        pass


###### Small scenery subclass ###### 
    

class SmallScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict):
        super().__init__(data, sprites)
        if data:
            if data['objectType'] != 'scenery_small':
                raise TypeError("Object is not small scenery.")

            self.size = (1, 1, int(self.data['properties']['height']/8))
            if data['properties'].get('isAnimated', False):
                self.subtype = self.Subtype.ANIMATED
            elif data['properties'].get('hasGlass', False):
                self.subtype = self.Subtype.GLASS
            elif data['properties'].get('canWither', False):
                self.subtype = self.Subtype.GARDENS
            else:
                self.subtype = self.Subtype.SIMPLE

    def show(self, animation_frame: int = -1, wither: int = 0):
        """Still need to implement all possible animation cases and glass objects."""
        if self.subtype == self.Subtype.GARDENS:
            return self.sprites[list(self.sprites)[self.rotation+4*wither]].show(self.current_first_remap, self.current_second_remap, self.current_third_remap)
        else:
            return self.sprites[list(self.sprites)[self.rotation]].show(self.current_first_remap, self.current_second_remap, self.current_third_remap)

    def rotateObject(self, rot: int = 1):
        self.rotation = (self.rotation + rot) % 4
        
    def setCurrentRotationAsDefault(self):
        rot = self.rotation
        image_list = self.data['images']
        self.data['images'] = image_list[rot:] + image_list[:rot]
        self.rotation = 0
        
    class Subtype(Enum):
        SIMPLE = 'Simple'
        ANIMATED = 'Animated'
        GLASS = 'Glass'
        GARDENS = 'Gardens'

###### Large scenery subclass ###### 

class LargeScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict):
        super().__init__(data, sprites)
        if data:
            if data['objectType'] != 'scenery_large':
                raise TypeError("Object is not small scenery.")

            self.size = self.setSize()
            self.num_tiles = len(self.data['properties']['tiles'])
        
        if data['properties'].get('3dFont', False):
            self.subtype = self.Subtype.SIGN
            self.font = self.data['properties']['3dFont']
            self.glyphs = self.font['glyphs']
            self.num_glyph_sprites = self.font['numImages']*2*(2-int(self.font.get('isVertical', 0))) 

        else:
            self.subtype = self.Subtype.SIMPLE
            self.num_glyph_sprites = 0
        
    def setSize(self):
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

    def show(self):
        x_size, y_size, z_size = self.size
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


        for tile_index in drawing_order:
            tile = tiles[tile_index]
            y_base = y_baseline + int(tile['x']/2) + int(tile['y']/2) - tile.get('z',0)
            x_base = x_baseline - tile['x'] + tile['y']

            sprite_index = 4 + 4*tile_index + view + self.num_glyph_sprites
            sprite = self.sprites[self.data['images'][sprite_index]['path']]
            canvas.paste(sprite.show(self.current_first_remap, self.current_second_remap, self.current_third_remap),
                         (x_base+sprite.x, y_base+sprite.y), sprite.image)

        return canvas.crop(canvas.getbbox())

    def rotateObject(self, rot: int = 1):
        self.rotation = (self.rotation + rot) % 4
        if self.num_tiles == 1:
            return

        rot_mat = matrix_power(np.array([[0, 1], [-1, 0]]), rot % 4)

        for tile in self.data['properties']['tiles']:
            pos = np.array([tile['x'], tile['y']])

            pos = rot_mat.dot(pos)
            tile['x'], tile['y'] = int(pos[0]), int(pos[1])
            
    def updateSpritesList(self):
        if self.subtype == self.Subtype.SIGN:
            self.sprites = self.glyphs_sprites.append(self.sprites)


    def getDrawingOrder(self):
        order = {}

        for tile_index, tile in enumerate(self.data['properties']['tiles']):
            score = tile['x'] + tile['y']
            order[tile_index] = score

        return sorted(order, key=order.get)

    def createThumbnails(self):
        if self.subtype != self.Subtype.SIGN:
            for rot in range(4):
                im = self.data['images'][rot]
                image = self.show()
                image.thumbnail((64, 112), Image.NEAREST)
                x = -int(image.size[0]/2)
                y = image.size[1]
                self.sprites[im['path']] = spr.Sprite(image, (x, y))
                self.rotateObject()
        else:
            raise NotImplementedError("Creating thumbnails is not supported yet for 3d sign objects.")
            
    class Subtype(Enum):
        SIMPLE = 'Simple'
        SIGN = '3D Sign'



# Wrapper to load any object type and instantiate is as the correct subclass

def load(filepath: str):
    """Instantiates a new object from a .parkobj  or .dat file."""
    extension = splitext(filepath)[1].lower()
    
    if extension == '.parkobj':
        obj = RCTObject.fromParkobj(filepath)
    elif extension == '.dat':
        obj = RCTObject.fromDat(filepath)
    elif extension == '.json':
        obj = RCTObject.fromJson(filepath)
    else:
        raise RuntimeError("Unsupported object file type.")

    obj_type = obj.data.get("objectType", False)
    if obj_type == 'scenery_small':
        return SmallScenery(obj.data,obj.sprites)
    elif obj_type == 'scenery_large':
        return LargeScenery(obj.data,obj.sprites)
    else:
        raise NotImplementedError("Object type unsupported by now.")

def new(data, sprites):
    """Instantiates a new object from given data and sprites."""

    obj_type = data.get("objectType", False)
    if obj_type == 'scenery_small':
        return SmallScenery(data,sprites)
    elif obj_type == 'scenery_large':
        return LargeScenery(data,sprites)
    else:
        raise NotImplementedError("Object type unsupported by now.")