"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************

Module for handling base classes of RCT objects.
Includes file handling (save/open) functions.

Objects may be loaded with from_parkobj and from_dat functions.

JSON data may be accessed and edited as dictionary key: obj[key]

Created 09/26/2021; 16:58:33

"""

from json import dump, loads
from json import load as jload
from os import mkdir, makedirs, replace, getcwd, remove, walk
from os import mkdir, makedirs, replace, getcwd, remove, walk
from os.path import splitext, exists
from pkgutil import get_data
import copy
from PIL import Image, ImageDraw
from shutil import unpack_archive, make_archive, move, rmtree
from tempfile import TemporaryDirectory
from subprocess import run
import numpy as np
from enum import Enum

import rctobject.sprites as spr
import rctobject.palette as pal
import rctobject.datloader as dat
import rctobject.constants as cts

OPENRCTPATH = '%USERPROFILE%\\Documents\\OpenRCT2'


def is_power_of_two(n):
    return (n != 0) and (n & (n-1) == 0)


class Type(Enum):
    SMALL = 'scenery_small'
    LARGE = 'scenery_large'
    WALL = "scenery_wall"
    BANNER = "footpath_banner"
    PATH = "footpath"
    PATHITEM = "footpath_item"
    GROUP = "scenery_group"
    ENTRANCE = "park_entrance"
    PALETTE = "water"
    TEXT = "scenario text"


class RCTObject:
    """Base class for all editable objects; loads from .parkobj or .DAT files."""

    def __init__(self, data: dict, sprites: dict, old_id=None):
        """Instantiate object directly given JSON and image data."""
        self.data = data
        self.sprites = sprites
        self.old_id = old_id

        self.object_type = None  # to be set in subclass

        self.rotation = 0

        self.palette = pal.orct
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
            o = cls.fromJson(f'{temp}/object.json', openpath)

        return o

    @classmethod
    def fromJson(cls, filepath: str, openpath: str = OPENRCTPATH):
        """Instantiates a new object from a .json file. openpath has to be according to the system's 
           openrct2 folder location if sprite refers to a dat-file."""

        filename_len = len(filepath.split('/')[-1])
        # trailing '/' included
        folder_path = filepath[:-filename_len]

        data = jload(fp=open(filepath, encoding='utf8'))
        dat_id = data.get('originalId', None)
        # If an original Id was given we load the sprites from original DATs (aka "official" openRCT objects).

        # check if any LGX sprites are in the object folder and pre-load them
        lgx_buffer = {}
        for file in next(walk(folder_path))[2]:
            if file.endswith('.lgx'):
                lgx_buffer[splitext(file)[0]] = dat.import_lgx(
                    f'{folder_path}{file}')

        # REWORK
        if isinstance(data['images'][0], str) and dat_id:
            dat_id = dat_id.split('|')[1].replace(' ', '')
            data['images'], sprites = dat.import_sprites_with_open(
                dat_id, openpath)

        # If no original dat is given, the images are assumed to lie in the relative path given in the json (unzipped parkobj).
        # The file is assumed to be called "object.json" in this case.
        elif isinstance(data['images'], list):
            images = []
            sprites = {}
            i = 0
            for im in data['images']:
                if isinstance(im, dict):
                    sprites[f'images/{i}.png'] = spr.Sprite.fromFile(
                        f'{folder_path}{im["path"]}', coords=(im['x'], im['y']), already_palettized=True)
                    im['path'] = f'images/{i}.png'
                    images.append(im)
                    i += 1
                elif isinstance(im, str) and im == '':
                    im = {}
                    im['x'] = 0
                    im['y'] = 0
                    sprites[f'images/{i}.png'] = spr.Sprite(None)
                    im['path'] = f'images/{i}.png'
                    images.append(im)
                    i += 1
                elif isinstance(im, str) and im.startswith('$LGX:'):
                    source = im[5:im.find(".lgx")]
                    index_range = im[im.find('[')+1:-1].split('..')
                    indices = [k for k in range(
                        int(index_range[0]), int(index_range[-1])+1)]

                    for index in indices:
                        im = copy.copy(lgx_buffer[source][0][index])
                        sprite = copy.copy(lgx_buffer[source][1][im['path']])
                        im['path'] = f'images/{i}.png'
                        sprites[im['path']] = sprite
                        images.append(im)
                        i += 1
                else:
                    raise RuntimeError(
                        'Image was not a valid type. G1, G2, CSG not supported')

            data['images'] = images

        elif isinstance(data['images'], str):
            s = data['images']
            images = []
            sprites = {}
            i = 0
            if s.startswith('$LGX:'):
                source = s[5:s.find(".lgx")]
                index_range = s[s.find('[')+1:-1].split('..')
                indices = [k for k in range(
                    int(index_range[0]), int(index_range[-1])+1)]

                for index in indices:
                    im = copy.copy(lgx_buffer[source][0][index])
                    sprite = copy.copy(lgx_buffer[source][1][im['path']])
                    im['path'] = f'images/{i}.png'
                    sprites[im['path']] = sprite
                    images.append(im)
                    i += 1
            data['images'] = images

        else:
            raise RuntimeError('Cannot extract images.')

        return cls(data=data, sprites=sprites, old_id=dat_id)

    @classmethod
    def fromDat(cls, filepath: str):
        """Instantiates a new object from a .DAT file."""

        data, sprites = dat.loadDatObject(filepath)
        dat_id = data['originalId'].split('|')[1].replace(' ', '')

        return cls(data=data, sprites=sprites, old_id=dat_id)

    def save(self, path: str = None, name: str = None, no_zip: bool = False, include_originalId: bool = False, compress_sprites: bool = False, openpath: str = OPENRCTPATH):
        """Saves an object as .parkobj file to specified path."""

        if not self.data.get('id', False):
            raise RuntimeError('Forbidden to save object without id!')

        # Reset object to default rotation
        self.setRotation(0)

        # If sprites have changed, they have to be updated
        self.updateImageList()
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
        if self.data.get('sceneryGroup') == '' or self.data.get('sceneryGroup') == '\x00\x00\x00\x00\x00\x00\x00\x00':
            self.data.pop('sceneryGroup')

        # All objects we save are custom objects
        self.data['sourceGame'] = "custom"

        if name:
            filename = f'{path}/{name}'
        else:
            filename = f'{path}/{self.data["id"]}'
            name = self.data["id"]

        data_save = copy.deepcopy(self.data)

        with TemporaryDirectory() as temp:
            mkdir(f'{temp}/images')
            if compress_sprites:
                im_list = self.data['images']
                for i, im in enumerate(self['images']):
                    sprite = self.sprites[im['path']]

                    sprite.save(f"{temp}/{im['path']}")

                with open(f'{temp}/sprites.json', mode='w') as file:
                    dump(obj=im_list, fp=file, indent=2)

                result = run([f'{openpath}/bin/openrct2', 'sprite',
                              'build', f'{temp}/sprites.lgx', f'{temp}/sprites.json'], stdout=-1, stderr=-1, encoding='utf-8')

                if result.returncode:
                    raise RuntimeError(
                        f'OpenRCT2 export error: {result.stderr}.')
                data_save['images'] = f"$LGX:sprites.lgx[0..{len(im_list)-1}]"

                remove(f'{temp}/sprites.json')
                rmtree(f'{temp}/images', ignore_errors=True)
            else:
                for i, im in enumerate(self['images']):
                    sprite = self.sprites[im['path']]

                    # we don't save empty sprites and replace their list entry with an empty string
                    if sprite.isEmpty():
                        data_save['images'][i] = ""
                    else:
                        sprite.save(f"{temp}/{im['path']}")

            with open(f'{temp}/object.json', mode='w') as file:
                dump(obj=data_save, fp=file, indent=2)

            make_archive(base_name=f'{filename}',
                         root_dir=temp, format='zip')

            replace(f'{filename}.zip', f'{filename}.parkobj')
            if no_zip:
                rmtree(filename, ignore_errors=True)
                makedirs(filename, exist_ok=True)

                if compress_sprites:
                    move(f'{temp}/sprites.lgx', filename)
                else:
                    move(f'{temp}/images', filename)

                move(f'{temp}/object.json', filename)

    def size(self):
        'gives size in game coordinates; to be defined in subclass'
        pass

    def spriteBoundingBox(self, view: int = None):
        if view is None:
            view = self.rotation

        x, y, z = self.size()

        height = int(-1 + x*16 + y*16 + z*8)
        width = int(x*32 + y*32)

        return (width, height)

    def switchPalette(self, palette):
        self.palette = palette
        for _, sprite in self.sprites.items():
            sprite.switchPalette(palette)

    def changeRemap(self, color, remap):
        if color:
            if remap == '1st Remap':
                self.current_first_remap = color
            elif remap == '2nd Remap':
                self.current_second_remap = color
            elif remap == '3rd Remap':
                self.current_third_remap = color

    def changeFlag(self, flag, value):
        self.data['properties'][flag] = value

    def updateImageOffsets(self):
        for im in self.data['images']:
            im['x'] = self.sprites[im['path']].x
            im['y'] = self.sprites[im['path']].y

    def updateImageList(self):
        new_dict = {}

        for i, im in enumerate(self['images']):
            sprite = self.sprites[im['path']]
            im['path'] = f'images/{i}.png'
            new_dict[im['path']] = sprite

        self.sprites = new_dict

    def setSpriteFromIndex(self, sprite_in: spr.Sprite, sprite_index: int):
        self.sprites[self.data['images'][sprite_index]
                     ['path']].setFromSprite(sprite_in.image)

    def changeFlag(self, flag, value):
        self.data['properties'][flag] = value

###### Small scenery subclass ######


class SmallScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict, old_id=None):
        super().__init__(data, sprites, old_id)
        if data:
            if data['objectType'] != 'scenery_small':
                raise TypeError("Object is not small scenery.")

            self.object_type = Type.SMALL
            self.has_preview = False
            self.num_image_sets = 1

            if data['properties'].get('isAnimated', False):
                self.subtype = self.Subtype.ANIMATED
                self.has_preview = data['properties'].get(
                    'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False) or data['properties'].get(
                    'SMALL_SCENERY_FLAG17', False)
                self.preview_backup = {}

                if data['properties'].get('SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1'):
                    self.animation_type = self.AnimationType.FOUNTAIN1
                    self.num_image_sets = 4
                elif data['properties'].get('SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4'):
                    self.animation_type = self.AnimationType.FOUNTAIN4
                    self.num_image_sets = 4
                elif data['properties'].get('isClock'):
                    self.animation_type = self.AnimationType.CLOCK
                    self.num_image_sets = 110
                elif data['properties'].get('SMALL_SCENERY_FLAG_SWAMP_GOO'):
                    self.animation_type = self.AnimationType.SINGLEVIEW
                    self.num_image_sets = 16
                else:
                    self.animation_type = self.AnimationType.REGULAR

                    while not is_power_of_two(len(data['properties']['frameOffsets'])):
                        data['properties']['frameOffsets'].append(0)

                    data['properties']['numFrames'] = len(
                        data['properties']['frameOffsets'])
                    self.num_image_sets = int(
                        len(data['images'])/4) - int(self.has_preview)

            elif data['properties'].get('hasGlass', False):
                self.subtype = self.Subtype.GLASS
                for rot in range(4):
                    sprite = self.giveSprite(rotation=rot, glass=True)
                    sprite.image = pal.colorAllVisiblePixels(
                        sprite.image, sprite.palette.getColor('1st Remap')[5])
            elif data['properties'].get('canWither', False):
                self.subtype = self.Subtype.GARDENS
            else:
                self.subtype = self.Subtype.SIMPLE

            shape = data['properties'].get('shape', False)
            if shape == '2/4':
                self.shape = self.Shape.HALF
            elif shape == '3/4+D':
                self.shape = self.Shape.THREEQ
            elif shape == '4/4':
                self.shape = self.Shape.FULL
            elif shape == '4/4+D':
                self.shape = self.Shape.FULLD
            elif shape == '1/4+D':
                self.shape = self.Shape.QUARTERD
            else:
                self.shape = self.Shape.QUARTER

            # Adjust sprite offsets from flags
            if self.shape == self.Shape.FULL or self.shape == self.Shape.FULLD or self.shape == self.Shape.THREEQ:
                if self.data['properties'].get('SMALL_SCENERY_FLAG_VOFFSET_CENTRE', False):
                    offset = 12
                    offset += 2 if self.data['properties'].get(
                        'prohibitWalls', False) else 0

                    for _, sprite in self.sprites.items():
                        sprite.overwriteOffsets(
                            int(sprite.x), int(sprite.y) - offset)

            elif self.shape == SmallScenery.Shape.HALF:
                offset = 12

                for _, sprite in self.sprites.items():
                    sprite.overwriteOffsets(
                        int(sprite.x), int(sprite.y) - offset)

    def size(self):
        if self.shape == self.Shape.HALF:
            size = (1, 1, int(self.data['properties']['height']/8))
        elif self.shape == self.Shape.THREEQ:
            size = (1, 1, int(self.data['properties']['height']/8))
        elif self.shape == self.Shape.FULL:
            size = (1, 1, int(self.data['properties']['height']/8))
        elif self.shape == self.Shape.FULLD:
            size = (1, 1, int(self.data['properties']['height']/8))
        elif self.shape == self.Shape.QUARTERD:
            size = (0.5, 0.5, int(
                self.data['properties']['height']/8))
        else:
            size = (0.5, 0.5, int(self.data['properties']['height']/8))

        return size

    def updateImageOffsets(self):
        """Override method from base class."""

        # Adjust sprite offsets from flags
        if (self.shape == self.Shape.FULL or self.shape == self.Shape.FULLD or self.shape == self.Shape.THREEQ) and self.data['properties'].get('SMALL_SCENERY_FLAG_VOFFSET_CENTRE', False):
            offset = 12
            offset += 2 if self.data['properties'].get(
                'prohibitWalls', False) else 0

        elif self.shape == SmallScenery.Shape.HALF:
            offset = 12

        else:
            offset = 0

        for im in self.data['images']:
            sprite = self.sprites[im['path']]

            im['x'] = sprite.x
            im['y'] = sprite.y + offset

    def show(self, rotation=None, animation_frame: int = 0, wither: int = 0, glass: bool = True, no_remaps=False):
        """Still need to implement all possible animation cases and glass objects."""

        if no_remaps:
            first_remap = 'NoColor'
            second_remap = 'NoColor'
            third_remap = 'NoColor'
        else:
            first_remap = self.current_first_remap
            second_remap = self.current_second_remap
            third_remap = self.current_third_remap

        if self.subtype == self.Subtype.GLASS and glass:
            if isinstance(rotation, int):
                rotation = rotation % 4
            else:
                rotation = self.rotation

            sprite_index = rotation
            mask_index = rotation+4
            sprite = self.sprites[self.data['images'][sprite_index]['path']]
            mask = self.sprites[self.data['images'][mask_index]['path']]

            color_remap = first_remap if first_remap != 'NoColor' else '1st Remap'
            image_paste = spr.colorAllInRemap(
                sprite.show('NoColor', second_remap,
                            third_remap),
                color_remap, sprite.palette)

            s1 = mask
            s2 = sprite

            canvas_size_x = max(abs(s1.x), abs(s1.image.width+s1.x),
                                abs(s2.x), abs(s2.image.width+s2.x))
            canvas_size_y = max(abs(s1.y), abs(s1.image.height+s1.y),
                                abs(s2.y), abs(s2.image.height+s2.y))

            canvas = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))
            canvas_top = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))
            canvas_top2 = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))
            canvas_mask = Image.new(
                '1', (canvas_size_x*2, canvas_size_y*2), color=0)

            color = sprite.palette.getRemapColor(color_remap)[5]
            canvas_mask.paste(1, (s1.x + canvas_size_x, s1.y + canvas_size_y),
                              mask=s1.image)
            canvas_top.paste(image_paste, (s2.x+canvas_size_x,
                             s2.y+canvas_size_y), mask=image_paste)

            canvas.paste(s2.show('NoColor', second_remap, third_remap),
                         (s2.x+canvas_size_x, s2.y+canvas_size_y), mask=s2.image)
            canvas.paste((color[0], color[1], color[2], 124), (s1.x + canvas_size_x, s1.y + canvas_size_y),
                         mask=s1.image)
            canvas_top2.paste(canvas_top, mask=canvas_mask)

            canvas = Image.alpha_composite(canvas, canvas_top2)
            bbox = canvas.getbbox()

            if bbox:
                canvas = canvas.crop(bbox)
                x = -canvas_size_x + bbox[0]
                y = -canvas_size_y + bbox[1]
            else:
                x, y = 0, 0

            return canvas, x, y
        elif self.subtype == self.Subtype.ANIMATED and self.animation_type in [self.AnimationType.FOUNTAIN1, self.AnimationType.FOUNTAIN4]:
            if isinstance(rotation, int):
                rotation = rotation % 4
            else:
                rotation = self.rotation

            base_index = rotation
            fountain_index = rotation+4*(animation_frame+1)
            fountain_index += 4 if self.animation_type == self.AnimationType.FOUNTAIN4 else 0

            s1 = self.sprites[self.data['images'][base_index]['path']]
            s2 = self.sprites[self.data['images'][fountain_index]['path']]

            canvas_size_x = max(abs(s1.x), abs(s1.image.width+s1.x),
                                abs(s2.x), abs(s2.image.width+s2.x))
            canvas_size_y = max(abs(s1.y), abs(s1.image.height+s1.y),
                                abs(s2.y), abs(s2.image.height+s2.y))

            if self.animation_type == self.AnimationType.FOUNTAIN4:
                s3 = self.sprites[self.data['images'][base_index+4]['path']]
                s4 = self.sprites[self.data['images']
                                  [fountain_index+16]['path']]

                canvas_size_x = max(abs(s3.x), abs(s3.image.width+s3.x),
                                    abs(s4.x), abs(s4.image.width+s4.x), canvas_size_x)
                canvas_size_y = max(abs(s3.y), abs(s3.image.height+s3.y),
                                    abs(s4.y), abs(s4.image.height+s4.y), canvas_size_y)

            canvas = Image.new('RGBA', (canvas_size_x*2, canvas_size_y*2))

            canvas.paste(s1.show(first_remap, second_remap, third_remap),
                         (s1.x+canvas_size_x, s1.y+canvas_size_y), mask=s1.image)
            canvas.paste(s2.show(first_remap, second_remap, third_remap),
                         (s2.x+canvas_size_x, s2.y+canvas_size_y), mask=s2.image)

            if self.animation_type == self.AnimationType.FOUNTAIN4:

                canvas.paste(s3.show(first_remap, second_remap, third_remap),
                             (s3.x+canvas_size_x, s3.y+canvas_size_y), mask=s3.image)
                canvas.paste(s4.show(first_remap, second_remap, third_remap),
                             (s4.x+canvas_size_x, s4.y+canvas_size_y), mask=s4.image)

            bbox = canvas.getbbox()

            if bbox:
                canvas = canvas.crop(bbox)
                x = -canvas_size_x + bbox[0]
                y = -canvas_size_y + bbox[1]
            else:
                x, y = 0, 0

            return canvas, x, y

        else:
            sprite = self.giveSprite(rotation, animation_frame, wither)
            return sprite.show(
                first_remap, second_remap, third_remap), sprite.x, sprite.y

    def giveIndex(self, rotation=None, animation_frame: int = 0, wither: int = 0, glass: bool = False):
        if isinstance(rotation, int):
            rotation = rotation % 4
        else:
            rotation = self.rotation

        if self.subtype == self.Subtype.GARDENS:
            if wither > 2:
                raise RuntimeError("Wither cannot be larger than 2.")
            sprite_index = rotation+4*wither
        elif self.subtype == self.Subtype.GLASS:
            sprite_index = rotation+4*int(glass)
        elif self.subtype == self.Subtype.ANIMATED:
            if self.animation_type == self.AnimationType.CLOCK and animation_frame > 1:
                sprite_index = 8+(animation_frame-2)
            elif self.animation_type == self.AnimationType.SINGLEVIEW:
                sprite_index = animation_frame
            else:
                sprite_index = rotation+4*animation_frame
        else:
            sprite_index = rotation

        return sprite_index

    def giveSprite(self, rotation=None, animation_frame: int = -1, wither: int = 0, glass: bool = False):
        """Still need to implement all possible animation cases and glass objects."""

        sprite_index = self.giveIndex(rotation, animation_frame, wither, glass)

        return self.sprites[self.data['images'][sprite_index]['path']]

    def setSprite(self, sprite_in: spr.Sprite, rotation: int = None, animation_frame: int = -1, wither: int = 0,
                  glass: bool = False):
        """Still need to implement all possible animation cases and glass objects."""

        sprite_index = self.giveIndex(rotation, animation_frame, wither, glass)

        self.setSpriteFromIndex(sprite_in, sprite_index)

    def rotateObject(self, rot: int = 1):
        self.rotation = (self.rotation + rot) % 4

    def setRotation(self, rot):
        self.rotateObject(rot-self.rotation)

    def cycleSpritesRotation(self, step: int = 1):
        for i in range(int(len(self.data['images'])/4)):
            image_list = self.data['images'][4*i:4*i+4]
            self.data['images'][4*i:4*i+4] = image_list[-step:] + \
                image_list[:-step]

        self.updateImageList()

    def addTile(self, coords, dict_entry=None):
        # we expect that the image list is ordered

        index = len(self.tiles)

        images = []
        for i in range(4):
            path = f'images/tile_{index}_im_{i}.png'
            try:
                im = self['images'][4*(index+1)+i]
            except IndexError:
                im = {'path': path, 'x': 0, 'y': 0}
                self.sprites[path] = spr.Sprite(None, (0, 0), self.palette)

            images.append(im)

        if not dict_entry:
            dict_entry = {'x': coords[0]*32,
                          'y': coords[1]*32,
                          'z': 0,
                          'clearance': 0,
                          'hasSupports': False,
                          'allowSupportsAbove': False,
                          'walls': 0,
                          'corners': 15}
        else:
            # we adjust the coordinates of the diven dict
            dict_entry['x'] = coords[0]*32
            dict_entry['y'] = coords[1]*32

        tile = self.Tile(self, dict_entry, images, self.rotation)
        self.tiles.append(tile)

    def removeTile(self, index):
        if index < 1:
            raise RuntimeError('Cannot remove anchor tile.')

        self.tiles.pop(index)

        self.updateImageList()

    # tbf
    def changeSubtype(self, subtype):
        if subtype == self.subtype:
            return

        self.subtype = subtype

        self.data['properties']['isAnimated'] = (
            self.subtype == self.Subtype.ANIMATED)
        self.data['properties']['hasGlass'] = (
            self.subtype == self.Subtype.GLASS)
        self.data['properties']['canWither'] = (
            self.subtype == self.Subtype.GARDENS)

        if subtype == self.Subtype.ANIMATED:
            self.animation_type = self.AnimationType.REGULAR
            self.data['properties']['frameOffsets'] = [0]
            self.data['properties']['animationDelay'] = 0
            self.data['properties']['animationMask'] = 0
            self.data['properties']['numFrames'] = 1
            self.has_preview = False
            self.preview_backup = {}

            self.num_image_sets = int(len(self.data['images'])/4)
        else:
            self.data['properties'].pop('frameOffsets', None)
            self.data['properties'].pop('animationDelay', None)
            self.data['properties'].pop('animationMask', None)
            self.data['properties'].pop('numFrames', None)
            for flag in cts.list_small_animation_flags:
                self.data['properties'].pop(flag, None)
            self.has_preview = False

        if subtype == self.Subtype.GLASS:
            if len(self.data['images'])/4 > 1:
                for rot in range(4):
                    sprite = self.giveSprite(rotation=rot, glass=True)
                    sprite.image = pal.colorAllVisiblePixels(
                        sprite.image, sprite.palette.getColor('1st Remap')[5])
            else:
                for rot in range(4):
                    path = f'images/{rot+4}.png'
                    im = {'path': path, 'x': 0, 'y': 0}
                    self.data['images'].append(im)
                    self.sprites[path] = spr.Sprite(None, (0, 0), self.palette)

        if subtype == self.Subtype.GARDENS:
            if len(self.data['images'])/4 < 3:
                num_spr = 3 - int(len(self.data['images'])/4)
                start_index = len(self.data["images"])
                for wither in range(num_spr):
                    for rot in range(4):
                        path = f'images/{wither*4+rot+start_index}.png'
                        im = {'path': path, 'x': 0, 'y': 0}
                        self.data['images'].append(im)
                        self.sprites[path] = spr.Sprite(
                            None, (0, 0), self.palette)

        if subtype == self.Subtype.SIMPLE:
            self.data['images'] = self.data['images'][:4]

        self.updateImageList()

    def changeShape(self, shape):
        self.shape = shape
        self.data['properties']['shape'] = shape.fullname

        # quarter is a default
        if shape == self.Shape.QUARTER:
            self.data['properties'].pop('shape')

    def changeAnimationType(self, anim_type):
        if self.animation_type == anim_type:
            return

        self.animation_type = anim_type

        self.data['properties']['SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1'] = (
            self.animation_type == self.AnimationType.FOUNTAIN1)
        self.data['properties']['SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4'] = (
            self.animation_type == self.AnimationType.FOUNTAIN4)
        self.data['properties']['isClock'] = (
            self.animation_type == self.AnimationType.CLOCK)
        self.data['properties']['SMALL_SCENERY_FLAG_SWAMP_GOO'] = (
            self.animation_type == self.AnimationType.SINGLEVIEW)

        if self.animation_type == self.AnimationType.REGULAR:
            self.data['properties']['frameOffsets'] = [0]
            self.data['properties']['animationDelay'] = 0
            self.data['properties']['animationMask'] = 0
            self.data['properties']['numFrames'] = 1
        else:
            self.data['properties'].pop('frameOffsets', None)
            self.data['properties'].pop('animationDelay', None)
            self.data['properties'].pop('animationMask', None)
            self.data['properties'].pop('numFrames', None)
            self.data['properties'].pop(
                'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', None)
            self.data['properties'].pop('SMALL_SCENERY_FLAG17', None)
            self.has_preview = False

        if self.animation_type == self.AnimationType.FOUNTAIN1:
            self.changeNumImagesSets(4)
        elif self.animation_type == self.AnimationType.FOUNTAIN4:
            self.changeNumImagesSets(4)
        elif self.animation_type == self.AnimationType.CLOCK:
            self.changeNumImagesSets(110)
        elif self.animation_type == self.AnimationType.SINGLEVIEW:
            self.changeNumImagesSets(16)
        else:
            self.has_preview = self.data['properties'].get(
                'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False) or self.data['properties'].get(
                'SMALL_SCENERY_FLAG17', False)
            self.changeNumImagesSets(
                int(len(self.data['images'])/4) - int(self.has_preview))

    def changeNumImagesSets(self, value):
        shift = int(self.has_preview)
        shift += 1 if self.animation_type == self.AnimationType.FOUNTAIN1 else 0
        shift += 6 if self.animation_type == self.AnimationType.FOUNTAIN4 else 0
        shift += 8 if self.animation_type == self.AnimationType.CLOCK else 0

        multiplier = 1 if self.animation_type in [
            self.AnimationType.CLOCK, self.AnimationType.SINGLEVIEW] else 4

        if len(self.data['images']) < (value+shift)*multiplier:
            index = len(self.data['images'])
            while index < (value+shift)*multiplier:
                im = {'path': f'images/{index}.png', 'x': 0, 'y': 0}
                self.data['images'].append(im)
                if not self.sprites.get(im['path'], False):
                    self.sprites[im['path']] = spr.Sprite(None)
                index += 1
        else:
            self.data['images'] = self.data['images'][:(
                value+shift)*multiplier]

            if self.animation_type == self.AnimationType.REGULAR:
                self.data['properties']['frameOffsets'] = [
                    value-1 if x == self.num_image_sets-1 else x for x in self.data['properties']['frameOffsets']]

        self.num_image_sets = value

        self.updateImageList()

    def updateAnimPreviewImage(self):
        new_has_preview = self.data['properties'].get(
            'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False) or self.data['properties'].get(
            'SMALL_SCENERY_FLAG17', False)
        if not new_has_preview == self.has_preview:
            self.has_preview = new_has_preview
            if self.has_preview:
                previews = [{'path': f'pre{i}', 'x': 0, 'y': 0}
                            for i in [0, 1, 2, 3]]
                self['images'] = previews + self['images']
                for im in previews:
                    self.sprites[im['path']] = self.preview_backup.get(
                        im['path'], spr.Sprite(None, (0, 0), palette=self.palette))
            else:
                for i, im in enumerate(self['images'][:4]):
                    sprite = self.sprites.pop(im['path'])
                    self.preview_backup[f'pre{i}'] = sprite

                self['images'] = self['images'][4:]

        self.updateImageList()

    def cycleAnimationFrame(self, view=-1):
        shift = int(self.has_preview)
        shift += 1 if self.animation_type == self.AnimationType.FOUNTAIN1 else 0
        shift += 2 if self.animation_type == self.AnimationType.FOUNTAIN4 else 0
        shift += 8 if self.animation_type == self.AnimationType.CLOCK else 0
        step = 1 if self.animation_type in [
            self.AnimationType.CLOCK, self.AnimationType.SINGLEVIEW] else 4

        shift = step*shift

        # case cycle all views
        if view == -1:
            image_list = self.data['images'][shift:]
            if self.animation_type == self.AnimationType.FOUNTAIN4:
                fountain1 = image_list[:16]
                fountain2 = image_list[16:]

                self.data['images'][shift:] = fountain1[-step:] + \
                    fountain1[:-step] + fountain2[-step:] + fountain2[:-step]
            else:
                self.data['images'][shift:] = image_list[-step:] + \
                    image_list[:-step]
        # case just one view
        else:
            image_list = self.data['images'][shift+view::step]
            if self.animation_type == self.AnimationType.FOUNTAIN4:
                fountain1 = image_list[:4]
                fountain2 = image_list[4:]

                self.data['images'][shift+view::step] = fountain1[-1:] + \
                    fountain1[:-1] + fountain2[-1:] + fountain2[:-1]
            else:
                self.data['images'][shift+view::step] = image_list[-1:] + \
                    image_list[:-1]

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

    class AnimationType(Enum):
        REGULAR = 0, 'Regular'
        FOUNTAIN1 = 1, 'Fountain 1'
        FOUNTAIN4 = 2, 'Fountain 4'
        CLOCK = 3, 'Clock'
        SINGLEVIEW = 4, 'Single View'

        def __new__(cls, value, name):
            member = object.__new__(cls)
            member._value_ = value
            member.fullname = name
            return member

        def __int__(self):
            return self.value

###### Large scenery subclass ######


class LargeScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict, old_id=None):
        super().__init__(data, sprites, old_id)
        if data:
            if data['objectType'] != 'scenery_large':
                raise TypeError("Object is not large scenery.")

            self.object_type = Type.LARGE

            if data['properties'].get('3dFont', False):
                self.subtype = self.Subtype.SIGN
                self.font = self.data['properties']['3dFont']
                self.glyphs = self.font['glyphs']
                self.num_glyph_sprites = self.font['numImages'] * \
                    2*(2-int(self.font.get('isVertical', 0)))
            else:
                self.subtype = self.Subtype.SIMPLE
                self.num_glyph_sprites = 0

            for _, sprite in self.sprites.items():
                sprite.overwriteOffsets(
                    int(sprite.x), int(sprite.y) - 15)

            self.tiles = []
            for i, tile_dict in enumerate(self['properties']['tiles']):
                tile = self.Tile(o=self, dict_entry=tile_dict,
                                 images=self['images']
                                 [4 * (i + 1) + self.num_glyph_sprites: 4 * (i + 2) + self.num_glyph_sprites],
                                 rotation=self.rotation)
                self.tiles.append(tile)

            self.updateImageList()

    def save(self, path: str = None, name: str = None, no_zip: bool = False,   include_originalId: bool = False, compress_sprites: bool = False, openpath: str = OPENRCTPATH):
        self.setRotation(0)
        tile_list = []
        for tile in self.tiles:
            tile_list.append(tile.giveDictEntry())

        self['properties']['tiles'] = tile_list

        super().save(path, name, no_zip, include_originalId, compress_sprites, openpath)

    def size(self):
        max_x = 0
        max_y = 0
        max_z = 0
        min_x = 0
        min_y = 0
        min_z = 0

        for tile in self.tiles:
            max_x = max(tile.x, max_x)
            max_y = max(tile.y, max_y)
            max_z = max(tile.z + tile.h, max_z)

            min_x = min(tile.x, min_x)
            min_y = min(tile.y, min_y)
            min_z = min(tile.z, min_z)

        x = max_x - min_x + 1
        y = max_y - min_y + 1
        z = max_z - min_z

        return (int(x), int(y), int(z))
    
    def baseCoordinates(self):
        # Coordinates of the base (0,0) tile in (unrotated) object space in tile grid coordinates from the object footprint
        rotation_save = int(self.rotation)
        self.setRotation(0)        
        min_x = 0
        min_y = 0
        

        for tile in self.tiles:
            min_x = min(tile.x, min_x)
            min_y = min(tile.y, min_y)
            
        self.setRotation(rotation_save)
        
        return int(min_x), int(min_y)

    def baseOffset(self):
        # Coordinates  of center of (0,0) tile in screen space of the sprite bounding box according to rotation
        max_x = 0
        max_y = 0
        max_z = 0
        min_x = 0
        min_y = 0
        min_z = 0

        for tile in self.tiles:
            max_x = max(tile.x, max_x)
            max_y = max(tile.y, max_y)
            max_z = max(tile.z + tile.h, max_z)

            min_x = min(tile.x, min_x)
            min_y = min(tile.y, min_y)
            min_z = min(tile.z, min_z)

        x = (max_x-min_y)*32+32
        y = (-min_x-min_y)*16+max_z*8+15

        return x, y

    def centerOffset(self):
        '''Coordinates of the center of ground base in screen space of the sprite bounding box according to rotation.'''

        x_obj, y_obj, z_obj = self.size()

        x = int(x_obj*16 + y_obj*16)
        y = int(-1 + x_obj*8 + y_obj*8 + z_obj*8)

        return x, y

    def show(self, rotation=None, no_remaps=False):
        if no_remaps:
            first_remap = 'NoColor'
            second_remap = 'NoColor'
            third_remap = 'NoColor'
        else:
            first_remap = self.current_first_remap
            second_remap = self.current_second_remap
            third_remap = self.current_third_remap

        tiles_list = self.getOrderedTileSprites(rotation)
        width, height, left, right, top, bottom = self.computeCanvasOverlap(
            tiles_list, rotation)
        canvas = Image.new('RGBA', (width, height))

        for tile_entry in tiles_list:
            sprite = tile_entry[0]
            canvas.paste(sprite.show(first_remap,
                                     second_remap,
                                     third_remap),
                         (tile_entry[1]+sprite.x+left, tile_entry[2]+sprite.y+top), sprite.image)

        x, y = self.centerOffset()

        return canvas, -x-left, -y-top

    def computeCanvasOverlap(self, tiles_list, rotation=None):
        'Computes the overlap of the object sprite to the sprite bounding box'
        left = 0
        right = 0
        top = 0
        bottom = 0

        width, height = self.spriteBoundingBox(rotation)

        for tile_entry in tiles_list:
            s = tile_entry[0]
            left = max(left, -s.x-tile_entry[1])
            right = max(right, s.image.width+s.x-(width-tile_entry[1]))
            top = max(top, -s.y-tile_entry[2])
            bottom = max(bottom, s.image.height+s.y-(height-tile_entry[2]))

        return (width+left+right, height+top+bottom, left, right, top, bottom)

    def rotateObject(self, rot: int = 1):
        self.rotation = (self.rotation + rot) % 4

        for tile in self.tiles:
            tile.rotate(rot)

    def setRotation(self, rot):
        self.rotateObject(rot-self.rotation)

    def getDrawingOrder(self, rotation=None):
        if rotation is not None:
            rotation_save = int(self.rotation)
            self.setRotation(rotation)
        else:
            rotation_save = None    
            
        order = {}

        for tile_index, tile in enumerate(self.tiles):
            score = tile.x + tile.y
            order[tile_index] = score
            
        if rotation_save is not None:
            self.setRotation(rotation_save)

        return sorted(order, key=order.get)

    def getOrderedTileSprites(self, rotation=None):
        if rotation is not None:
            rotation_save = int(self.rotation)
            self.setRotation(rotation)
        else:
            rotation_save = None

        x_baseline, y_baseline = self.baseOffset()

        tile_index = 0
        drawing_order = self.getDrawingOrder()

        ret = []

        for tile_index in drawing_order:
            tile = self.tiles[tile_index]
            y = y_baseline + \
                tile.x*16 + tile.y*16 - tile.z*8
            x = x_baseline - tile.x*32 + tile.y*32

            sprite = tile.giveSprite(rotation)

            ret.append([sprite, x, y, tile_index])

        if rotation_save is not None:
            self.setRotation(rotation_save)

        return ret

    def createThumbnails(self):
        if self.subtype != self.Subtype.SIGN:
            for rot in range(4):
                im = self.data['images'][rot]
                image = self.show()[0]
                bbox = image.getbbox()
                if bbox:
                    image = image.crop(bbox)

                image.thumbnail((64, 78), Image.NEAREST)
                x = -image.size[0]//2
                y = (78 - image.size[1])//2
                self.sprites[im['path']] = spr.Sprite(image, (x, y))
                self.rotateObject()
        else:
            raise NotImplementedError(
                "Creating thumbnails is not supported yet for 3d sign objects.")

    # Override base class
    def updateImageOffsets(self):
        offset = 15
        for im in self.data['images']:
            im['x'] = self.sprites[im['path']].x
            im['y'] = self.sprites[im['path']].y + offset

    def updateImageList(self):
        new_dict = {}
        new_list = []

        for view in range(4):
            im = self['images'][view]
            sprite = self.sprites.pop(im['path'])
            im['path'] = f'images/preview_{view}.png'
            new_dict[im['path']] = sprite
            new_list.append(im)

        for i, tile in enumerate(self.tiles):
            for view in range(4):
                im = tile.images[view]
                sprite = self.sprites.pop(im['path'], spr.Sprite(None, (0, 0), self.palette))
                im['path'] = f'images/tile_{i}_im_{view}.png'
                new_dict[im['path']] = sprite
                new_list.append(im)

        self['images'] = new_list
        self.sprites = new_dict

    def projectSpriteToTiles(self, sprite, rotation=None):
        x_baseline, y_baseline = self.centerOffset()

        if not sprite.palette == self.palette:
            sprite.switchPalette(self.palette)

        im_paste = Image.new('RGBA', self.spriteBoundingBox())
        im_paste.paste(
            sprite.image, (sprite.x+x_baseline, sprite.y+y_baseline))

        self.projectImageToTiles(im_paste, rotation, already_palettized=True)

    def projectImageToTiles(self, im_paste, rotation=None, already_palettized=False):
        rotation_save = int(self.rotation)

        if rotation is not None:
            self.setRotation(rotation)

        for i, tile in enumerate(self.tiles):
            im = Image.new('RGBA', self.spriteBoundingBox())
            mask = self.giveMask(tile)

            im.paste(im_paste, mask=mask)
            bbox = mask.getbbox()

            sprite_tile = spr.Sprite(
                im, coords=(-bbox[0]-32, -bbox[1]-tile.h*8-15), palette=self.palette, already_palettized=already_palettized)
            tile.setSprite(sprite_tile)

        self.setRotation(rotation_save)

    def giveMask(self, tile):
        x_baseline, y_baseline = self.baseOffset()

        mask = Image.new('1', self.spriteBoundingBox())
        draw = ImageDraw.Draw(mask)

        x = x_baseline - tile.x*32+tile.y*32-32
        y = y_baseline + tile.x*16+tile.y*16-tile.z*8

        for i in range(64):
            if i < 32:
                draw.line([(x+i, y-i//2-tile.h*8),
                           (x+i, y+i//2)],
                          fill=1, width=1)
            else:
                draw.line([(x+i, y-(63-i)//2-tile.h*8),
                           (x+i, y+(63-i)//2)],
                          fill=1, width=1)

        return mask
    
    def numTiles(self):
        return len(self.tiles)

    def addTile(self, coords, dict_entry=None, clearance=0):
        # we expect that the image list is ordered, coords are in unrotated object space
                
        if self.getTile(coords)[0]:
            raise RuntimeError(f'Tile at coordinates {coords} already exists.')

        index = len(self.tiles)

        images = []
        for i in range(4):
            path = f'images/tile_{index}_im_{i}.png'
            try:
                im = self['images'][4*(index+1)+i]
            except IndexError:
                im = {'path': path, 'x': 0, 'y': 0}
                self.sprites[path] = spr.Sprite(None, (0, 0), self.palette)

            images.append(im)

        if not dict_entry:
            dict_entry = {'x': coords[0]*32,
                          'y': coords[1]*32,
                          'z': 0,
                          'clearance': 0,
                          'hasSupports': False,
                          'allowSupportsAbove': False,
                          'walls': 0,
                          'corners': 15}
        else:
            # we adjust the coordinates of the diven dict
            dict_entry['x'] = coords[0]*32
            dict_entry['y'] = coords[1]*32

        if clearance:
            dict_entry['clearance'] = clearance*8

        tile = self.Tile(self, dict_entry, images, self.rotation)
        self.tiles.append(tile)
        

    def removeTile(self, index):
        if index < 1:
            raise RuntimeError('Cannot remove anchor tile.')

        self.tiles.pop(index)

        self.updateImageList()

    def getTile(self, coords):
        #corresponding in the original unrotated object space
        for i, tile in enumerate(self.tiles):
            if (tile.x_orig, tile.y_orig) == coords:
                return tile, i

        return None, None

    def fillShape(self, x_length, y_length, base_x = 0, base_y = 0, dict_entry=None, clearance=0):
        # fill a rectangular shape with tiles, where base_x and base_y are the coordinates of the base (0,0) tile in tile grid coordinates from the desired footprint
        for x in range(x_length):
            for y in range(y_length):
                if self.getTile((x-base_x, y-base_y))[0]:
                    continue

                self.addTile((x-base_x, y-base_y), dict_entry=dict_entry, clearance=clearance)
                
        self.updateImageList()
        
    def detectWalls(self):
        # detect walls for all tiles based on neighboring tiles 
        for tile in self.tiles:
            neighbor_coords = [(tile.x_orig-1, tile.y_orig),  # North
                               (tile.x_orig, tile.y_orig+1),  # East
                               (tile.x_orig+1, tile.y_orig),  # South
                               (tile.x_orig, tile.y_orig-1)]  # West

            for i, n_coords in enumerate(neighbor_coords):
                neighbor_tile, _ = self.getTile(n_coords)
                if neighbor_tile:
                    tile.walls[i] = False
                else:
                    tile.walls[i] = True

    def changeShape(self, width, length, height):
        # erase all tiles and set a rectangular shape

        for i in range(1, len(self.tiles)):
            self.removeTile(i)

        self.tiles[0].h = height

        for x in range(width):
            for y in range(length):
                if x == 0 and y == 0:
                    continue
                self.addTile((x, y), clearance=height)

        self.updateImageList()

    def copyTilesGeometry(self, tiles):
        tiles_copy = []
        
        for tile in tiles:
            tiles_copy.append(self.Tile(self, tile.giveDictEntry(), tile.images, rotation=self.rotation))

        self.tiles = tiles_copy
        self.updateImageList()
            

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

    class Tile:
        def __init__(self, o, dict_entry, images, rotation=0):
            self.o = o

            self.dict_entry = dict_entry
            self.x = dict_entry['x']//32
            self.x_orig = dict_entry['x']//32
            self.y = dict_entry['y']//32
            self.y_orig = dict_entry['y']//32
            self.z = dict_entry.get('z', 0)//8
            self.h = dict_entry['clearance']//8
            
            self.has_supports = dict_entry.get('hasSupports', False)
            self.allow_supports_above = dict_entry.get('allowSupportsAbove', False)
            self.walls = [bool(dict_entry.get('walls', 0) & 0x1),
                          bool(dict_entry.get('walls', 0) & 0x2),
                          bool(dict_entry.get('walls', 0) & 0x4),
                          bool(dict_entry.get('walls', 0) & 0x8)]
            self.corners = [bool(dict_entry.get('corners', 15) & 0x1),
                            bool(dict_entry.get('corners', 15) & 0x2),
                            bool(dict_entry.get('corners', 15) & 0x4),
                            bool(dict_entry.get('corners', 15) & 0x8)]

            self.images = images

            self.rotation = 0
            self.rotation_matrices = [
                np.array([[1, 0], [0, 1]]),   # R^0
                np.array([[0, 1], [-1, 0]]),  # R
                np.array([[-1, 0], [0, -1]]),  # R^2
                np.array([[0, -1], [1, 0]])   # R^3
            ]

            self.rotate(rotation)

        def rotate(self, rot):
            self.rotation = (self.rotation + rot) % 4

            rot_mat = self.rotation_matrices[rot % 4]

            pos = np.array([self.x, self.y])

            pos = rot_mat.dot(pos)
            self.x, self.y = int(pos[0]), int(pos[1])

        def giveSprite(self, rotation=None):
            if isinstance(rotation, int):
                rotation = rotation % 4
            else:
                rotation = self.rotation

            return self.o.sprites[self.images[rotation]['path']]

        def setSprite(self, sprite, rotation=None):
            if isinstance(rotation, int):
                rotation = rotation % 4
            else:
                rotation = self.rotation

            self.o.sprites[self.images[rotation]['path']].setFromSprite(sprite)

        def giveDictEntry(self):
            dict_entry = {}

            dict_entry['x'] = self.x*32
            dict_entry['y'] = self.y*32
            if self.z != 0:
                dict_entry['z'] = self.z*8
            dict_entry['clearance'] = self.h*8

            if self.has_supports:
                dict_entry['hasSupports'] = self.has_supports
            if self.allow_supports_above:
                dict_entry['allowSupportsAbove'] = self.allow_supports_above

            if self.giveWalls() != 15:
                dict_entry['walls'] = self.giveWalls()
            if self.giveCorners() != 0:
                dict_entry['corners'] = self.giveCorners()

            return dict_entry

        def giveWalls(self):
            return int(self.walls[0])+int(self.walls[1])*2 + int(self.walls[2])*4 + int(self.walls[3])*8

        def giveCorners(self):
            return int(self.corners[0])+int(self.corners[1])*2 + int(self.corners[2])*4 + int(self.corners[3])*8


# Wrapper to load any object type and instantiate it as the correct subclass

def load(filepath: str, openpath=OPENRCTPATH):
    """Instantiates a new object from a .parkobj  or .dat file."""
    extension = splitext(filepath)[1].lower()

    if extension == '.parkobj':
        obj = RCTObject.fromParkobj(filepath, openpath)
    elif extension == '.dat':
        obj = RCTObject.fromDat(filepath)
    elif extension == '.json':
        obj = RCTObject.fromJson(filepath, openpath)
    else:
        raise RuntimeError("Unsupported object file type.")

    obj_type = obj.data.get("objectType", False)
    if obj_type == 'scenery_small':
        return SmallScenery(obj.data, obj.sprites, obj.old_id)
    elif obj_type == 'scenery_large':
        return LargeScenery(obj.data, obj.sprites, obj.old_id)
    else:
        raise NotImplementedError(
            f"Object type {obj_type} unsupported by now.")


def loadFromId(identifier: str, openpath=OPENRCTPATH):
    filepath = f'{openpath}/object/{identifier}.DAT'

    if not exists(filepath):
        raise RuntimeError(f'Could not find DAT-object in specified OpenRCT2 path: \n \
                           "{filepath}"')

    obj = RCTObject.fromDat(filepath)

    obj_type = obj.data.get("objectType", False)
    if obj_type == 'scenery_small':
        return SmallScenery(obj.data, obj.sprites, obj.old_id)
    elif obj_type == 'scenery_large':
        return LargeScenery(obj.data, obj.sprites, obj.old_id)
    else:
        raise NotImplementedError(
            f"Object type {obj_type} unsupported by now.")


def new(data, sprites):
    """Instantiates a new object from given data and sprites."""

    object_type = data.get("objectType", False)
    if object_type == 'scenery_small':
        return SmallScenery(data, sprites)
    elif object_type == 'scenery_large':
        return LargeScenery(data, sprites)
    else:
        raise NotImplementedError(
            f"Object type {object_type} unsupported by now.")


def newEmpty(object_type: Type):
    """Instantiates a new empty object of given type."""

    data = {}

    if object_type == Type.SMALL:
        data = copy.deepcopy(cts.data_template_small)
    elif object_type == Type.LARGE:
        data = copy.deepcopy(cts.data_template_large)
    else:
        raise NotImplementedError(
            f"Object type {object_type.value} unsupported by now.")

    sprites = {im['path']: spr.Sprite(None) for im in data['images']}

    return new(data, sprites)
