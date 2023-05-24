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
from os import mkdir, makedirs, replace, getcwd
from os.path import splitext
import copy
from PIL import Image
from shutil import unpack_archive, make_archive, move, rmtree
from tempfile import TemporaryDirectory
from subprocess import run
import numpy as np
from enum import Enum

import rctobject.sprites as spr
import rctobject.datloader as dat
import rctobject.constants as cts

OPENRCTPATH = '%USERPROFILE%\\Documents\\OpenRCT2'


class RCTObject:
    """Base class for all editable objects; loads from .parkobj or .DAT files."""

    def __init__(self, data: dict, sprites: dict, old_id = None):
        """Instantiate object directly given JSON and image data."""
        self.data = data
        self.sprites = sprites
        self.old_id = old_id

        self.object_type = None # to be set in subclass

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
    def fromParkobj(cls, filepath: str, openpath: str = OPENRCTPATH):
        """Instantiates a new object from a .parkobj file."""
        with TemporaryDirectory() as temp:
            unpack_archive(filename=filepath, extract_dir=temp, format='zip')
            # Raises error on incorrect object structure or missing json:
            data = jload(fp=open(f'{temp}/object.json', encoding='utf-8'))
            dat_id = data.get('originalId',None)
            # If an original Id was given and the sprites are supposed to be loaded from the dat file we do so (aka "official" openRCT objects).
            if isinstance(data['images'][0], str) and dat_id:
                dat_id = dat_id.split('|')[1].replace(' ', '')
                with TemporaryDirectory() as temp:
                    temp = temp.replace('\\', '/')
                    result = run([f'{openpath}/bin/openrct2', 'sprite',
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
                sprites = {im['path']: spr.Sprite.fromFile(
                    f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}
            else:
                raise RuntimeError('Cannot extract images.')

        return cls(data=data, sprites=sprites, old_id = dat_id)

    @classmethod
    def fromJson(cls, filepath: str, openpath: str = OPENRCTPATH):
        """Instantiates a new object from a .json file. Sprite exporting is done
        by openRCT, hence openpath has to be according to the system's openrct2 folder location."""
        data = jload(fp=open(filepath, encoding='utf8'))
        dat_id = data.get('originalId',None)
        # If an original Id was given we load the sprites from original DATs (aka "official" openRCT objects).
        if isinstance(data['images'][0], str) and dat_id:
            dat_id = dat_id.split('|')[1].replace(' ', '')
            with TemporaryDirectory() as temp:
                temp = temp.replace('\\', '/')
                result = run([f'{openpath}/bin/openrct2', 'sprite',
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

        return cls(data=data, sprites=sprites, old_id = dat_id)

    @classmethod
    def fromDat(cls, filepath: str, openpath: str = OPENRCTPATH):
        """Instantiates a new object from a .DAT file. Sprite exporting is done
        by openRCT, hence openpath has to be according to the system's openrct2 folder location."""

        data = dat.read_dat_info(filepath)
        dat_id = data['originalId'].split('|')[1].replace(' ', '')
        with TemporaryDirectory() as temp:
            temp = temp.replace('\\', '/')
            result = run([f'{openpath}/bin/openrct2', 'sprite',
                         'exportalldat', dat_id, f'{temp}/images'], stdout=-1, encoding='utf-8')
            string = result.stdout
            string = string[string.find('{'):].replace(f'{temp}/', '')
            i = -1
            while string[i] != ',':
                i -= 1

            data['images'] = loads(f'[{string[:i]}]')
            sprites = {im['path']: spr.Sprite.fromFile(
                f'{temp}/{im["path"]}', coords=(im['x'], im['y'])) for im in data['images']}

        return cls(data=data, sprites=sprites, old_id = dat_id)


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

        # Remove all false flags to clean up the json
        for key, val in dict(self.data['properties']).items():
            if isinstance(val, bool) and val == False:
                self.data['properties'].pop(key)

        # Remove empty name strings
        for lang, lang_name in dict(self.data['strings']['name']).items():
            if lang == 'en-GB':
                continue

            if not lang_name:
                self.data['strings']['name'].pop(lang)

        # Remove an empty scenery group
        if self.data.get('sceneryGroup') == '' or  self.data.get('sceneryGroup') == '\x00\x00\x00\x00\x00\x00\x00\x00':
             self.data.pop('sceneryGroup')

        if name:
            filename = f'{path}/{name}'
        else:
            filename = f'{path}/{self.data["id"]}'
            name = self.data["id"]

        with TemporaryDirectory() as temp:
            mkdir(f'{temp}/images')
            with open(f'{temp}/object.json', mode='w') as file:
                dump(obj=self.data, fp=file, indent=2)
            for im_name, sprite in self.sprites.items():
                sprite.save(f'{temp}/{im_name}')
            make_archive(base_name=f'{filename}',
                         root_dir=temp, format='zip')

            replace(f'{filename}.zip', f'{filename}.parkobj')
            if no_zip:
                rmtree(filename, ignore_errors=True)
                makedirs(filename, exist_ok=True)
               # mkdir(f'{filename}/images')
                move(f'{temp}/images', filename)
                move(f'{temp}/object.json', filename)

    def spriteBoundingBox(self, view: int = None):
        if view is None:
            view = self.rotation

        x, y, z = self.size

        height = int(-1 + x*16 + y*16 + z*8)
        width = int(x*32 + y*32)

        return (width, height)

    def switchPalette(self, palette):
        for i, sprite in self.sprites.items():
            sprite.switchPalette(palette)

    def changeRemap(self, color, remap):
        if remap == '1st Remap':
            self.current_first_remap = color
        elif remap == '2nd Remap':
            self.current_second_remap = color
        elif remap == '3rd Remap':
            self.current_third_remap = color

    def updateImageOffsets(self):
        for im in self.data['images']:
            im['x'] = self.sprites[im['path']].x
            im['y'] = self.sprites[im['path']].y

    def updateSpritesList(self):
        pass


###### Small scenery subclass ######


class SmallScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict, old_id = None):
        super().__init__(data, sprites, old_id)
        if data:
            if data['objectType'] != 'scenery_small':
                raise TypeError("Object is not small scenery.")

            self.object_type = cts.Type.SMALL

            if data['properties'].get('isAnimated', False):
                self.subtype = self.Subtype.ANIMATED
            elif data['properties'].get('hasGlass', False):
                self.subtype = self.Subtype.GLASS
            elif data['properties'].get('canWither', False):
                self.subtype = self.Subtype.GARDENS
            else:
                self.subtype = self.Subtype.SIMPLE

            shape = data['properties'].get('shape', False)
            if shape == '2/4':
                self.shape = self.Shape.HALF
                self.size = (1, 1, int(self.data['properties']['height']/8))
            elif shape == '3/4+D':
                self.shape = self.Shape.THREEQ
                self.size = (1, 1, int(self.data['properties']['height']/8))
            elif shape == '4/4':
                self.shape = self.Shape.FULL
                self.size = (1, 1, int(self.data['properties']['height']/8))
            elif shape == '4/4+D':
                self.shape = self.Shape.FULLD
                self.size = (1, 1, int(self.data['properties']['height']/8))
            elif shape == '1/4+D':
                self.shape = self.Shape.QUARTERD
                self.size = (0.5, 0.5, int(self.data['properties']['height']/8))
            else:
                self.shape = self.Shape.QUARTER
                self.size = (0.5, 0.5, int(self.data['properties']['height']/8))

            # Adjust sprite offsets from flags
            if self.shape == self.Shape.FULL or self.shape == self.Shape.FULLD or self.shape == self.Shape.THREEQ:
                if self.data['properties'].get('SMALL_SCENERY_FLAG_VOFFSET_CENTRE', False):
                    offset = 12
                    offset += 2 if self.data['properties'].get('prohibitWalls', False) else 0

                    for _, sprite in self.sprites.items():
                        sprite.overwriteOffsets(int(sprite.x), int(sprite.y) - offset)

            elif self.shape == SmallScenery.Shape.HALF:
                offset = 12

                for _, sprite in self.sprites.items():
                    sprite.overwriteOffsets(int(sprite.x), int(sprite.y) - offset)


    def updateImageOffsets(self):
        """Override method from base class."""

        # Adjust sprite offsets from flags
        if (self.shape == self.Shape.FULL or self.shape == self.Shape.FULLD or self.shape == self.Shape.THREEQ ) and self.data['properties'].get('SMALL_SCENERY_FLAG_VOFFSET_CENTRE', False):
            offset = 12
            offset += 2 if self.data['properties'].get('prohibitWalls', False) else 0

        elif self.shape == SmallScenery.Shape.HALF:
            offset = 12

        else:
            offset = 0

        for im in self.data['images']:
            sprite = self.sprites[im['path']]

            im['x'] = sprite.x
            im['y'] = sprite.y + offset


    def show(self, rotation = None, animation_frame: int = -1, wither: int = 0):
        """Still need to implement all possible animation cases and glass objects."""

        if isinstance(rotation, int):
            rotation = rotation % 4
        else:
            rotation = self.rotation

        if self.subtype == self.Subtype.GARDENS:
            sprite_index = rotation+4*wither
        else:
            sprite_index = rotation

        sprite = self.sprites[self.data['images'][sprite_index]['path']]
        return sprite.show(self.current_first_remap, self.current_second_remap, self.current_third_remap), sprite.x, sprite.y
       # canvas.paste(sprite.show(self.current_first_remap, self.current_second_remap, self.current_third_remap),
     #                (x_base+sprite.x, y_base+sprite.y), sprite.image)

       # return canvas
    def giveSprite(self, rotation = None, animation_frame: int = -1, wither: int = 0, return_index = False):
        """Still need to implement all possible animation cases and glass objects."""

        if isinstance(rotation, int):
            rotation = rotation % 4
        else:
            rotation = self.rotation

        if self.subtype == self.Subtype.GARDENS:
            sprite_index = rotation+4*wither
        else:
            sprite_index = rotation

        if return_index:
            return self.sprites[self.data['images'][sprite_index]['path']], sprite_index
        else:
            return self.sprites[self.data['images'][sprite_index]['path']]

    def setSprite(self, sprite_in: spr.Sprite, rotation: int = None, animation_frame: int = -1, wither: int = 0):
        """Still need to implement all possible animation cases and glass objects."""
        sprite = copy.deepcopy(sprite_in)

        if isinstance(rotation, int):
            rotation = rotation % 4
        else:
            rotation = self.rotation

        if self.subtype == self.Subtype.GARDENS:
            sprite_index = rotation+4*wither
        else:
            sprite_index = rotation
        
        self.sprites[self.data['images'][sprite_index]['path']] = sprite

    def rotateObject(self, rot = None):
        if not isinstance(rot, int):
            self.rotation = (self.rotation + 1) % 4
        else:
            self.rotation = rot % 4

    def cycleSpritesRotation(self, step: int = 1):
        image_list = self.data['images']
        self.data['images'] = image_list[-step:] + image_list[:-step]

    def changeFlag(self, flag, value):
        self.data['properties'][flag] = value

    # tbf
    def changeSubtype(self, subtype):
        if subtype == self.subtype:
            return

    def changeShape(self, shape):
        self.shape = shape
        self.data['properties']['shape'] = shape.fullname



        # quarter is a default
        if shape == self.Shape.QUARTER:
            self.data['properties'].pop('shape')


    class Shape(Enum):
        QUARTER = 0, '1/4'
        HALF = 1, '2/4'
        THREEQ = 2, '3/4+D'
        FULL = 3, '4/4'
        FULLD = 4, '4/4+D'
        QUARTERD = 5, '1/4+D'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value



    class Subtype(Enum):
        SIMPLE = 0, 'Simple'
        ANIMATED = 1, 'Animated'
        GLASS = 2, 'Glass'
        GARDENS = 3, 'Gardens'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value

###### Large scenery subclass ######

class LargeScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict, old_id = None):
        super().__init__(data, sprites, old_id)
        if data:
            if data['objectType'] != 'scenery_large':
                raise TypeError("Object is not large scenery.")

            self.object_type = cts.Type.LARGE

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

        self.rotation_matrices = [
            np.array([[1,0],[0,1]]),      # R^0
            np.array([[0, 1], [-1, 0]]),  # R
            np.array([[-1, 0], [0, -1]]), # R^2
            np.array([[0, -1], [1, 0]])   # R^3
            ]

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

        return canvas

    def rotateObject(self, rot: int = 1):
        self.rotation = (self.rotation + rot) % 4
        if self.num_tiles == 1:
            return

        rot_mat = self.rotation_matrices[rot % 4]

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

    # Override base class
    def updateImageOffsets(self):
        for i, im in enumerate(self.data['images']):
            # Update the non-preview sprites
            if i >3:
                im['x'] = self.sprites[im['path']].x
                im['y'] = self.sprites[im['path']].y
            # preview sprites have different offsets
            else:
                image = self.sprites[im['path']].show()
                im['x'] = -int(image.size[0]/2)
                im['y'] = image.size[1]



    class Subtype(Enum):
        SIMPLE = 0, 'Simple'
        SIGN = 1, '3D Sign'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value



# Wrapper to load any object type and instantiate is as the correct subclass

def load(filepath: str, openpath = OPENRCTPATH):
    """Instantiates a new object from a .parkobj  or .dat file."""
    extension = splitext(filepath)[1].lower()

    if extension == '.parkobj':
        obj = RCTObject.fromParkobj(filepath, openpath)
    elif extension == '.dat':
        obj = RCTObject.fromDat(filepath, openpath)
    elif extension == '.json':
        obj = RCTObject.fromJson(filepath, openpath)
    else:
        raise RuntimeError("Unsupported object file type.")

    obj_type = obj.data.get("objectType", False)
    if obj_type == 'scenery_small':
        return SmallScenery(obj.data, obj.sprites, obj.old_id)
   # elif obj_type == 'scenery_large':
   #     return LargeScenery(obj.data, obj.sprites, obj.old_id)
    else:
        raise NotImplementedError(f"Object type {obj_type} unsupported by now.")

def loadFromId(identifier: str):
    pass

def new(data, sprites):
    """Instantiates a new object from given data and sprites."""

    object_type = data.get("objectType", False)
    if object_type == 'scenery_small':
        return SmallScenery(data, sprites)
    elif object_type == 'scenery_large':
        return LargeScenery(data, sprites)
    else:
        raise NotImplementedError(f"Object type {object_type} unsupported by now.")

def newEmpty(object_type: cts.Type):
    """Instantiates a new empty object of given type."""

    data = {}

    if object_type == cts.Type.SMALL:
        data = cts.data_template_small
    elif object_type == cts.Type.LARGE:
            data = cts.data_template_large
    else:
        raise NotImplementedError(f"Object type {object_type.value} unsupported by now.")



    sprites = {im['path']: spr.Sprite(None) for im in data['images']}

    return new(data,sprites)











