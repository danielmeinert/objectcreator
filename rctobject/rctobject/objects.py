"""
*****************************************************************************
 * Copyright (c) 2024 Tolsimir
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
from os import mkdir, makedirs, replace, getcwd
from os.path import splitext, exists
import copy
from PIL import Image
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
        data = jload(fp=open(filepath, encoding='utf8'))
        dat_id = data.get('originalId', None)
        # If an original Id was given we load the sprites from original DATs (aka "official" openRCT objects).
        if isinstance(data['images'][0], str) and dat_id:
            dat_id = dat_id.split('|')[1].replace(' ', '')
            data['images'], sprites = dat.import_sprites(dat_id, openpath)

        # If no original dat is given, the images are assumed to lie in the relative path given in the json (unzipped parkobj).
        # The file is assumed to be called "object.json" in this case.
        elif isinstance(data['images'][0], dict):
            sprites = {}
            filename_len = len(filepath.split('/')[-1])
            for i, im in enumerate(data['images']):
                if isinstance(im, dict):
                    sprites[f'images/{i}.png'] = spr.Sprite.fromFile(
                        f'{filepath[:-filename_len]}{im["path"]}', coords=(im['x'], im['y']))
                    im['path'] = f'images/{i}.png'
                elif isinstance(im, str) and im == '':
                    im = {}
                    im['x'] = 0
                    im['y'] = 0
                    sprites[f'images/{i}.png'] = spr.Sprite(None)
                    im['path'] = f'images/{i}.png'
                    data['images'][i] = im

        else:
            raise RuntimeError('Cannot extract images.')

        return cls(data=data, sprites=sprites, old_id=dat_id)

    @classmethod
    def fromDat(cls, filepath: str):
        """Instantiates a new object from a .DAT file."""

        data, sprites = dat.loadDatObject(filepath)
        dat_id = data['originalId'].split('|')[1].replace(' ', '')

        return cls(data=data, sprites=sprites, old_id=dat_id)

    def save(self, path: str = None, name: str = None, no_zip: bool = False, include_originalId: bool = False):
        """Saves an object as .parkobj file to specified path."""
        if not path:
            path = getcwd()

        if not self.data.get('id', False):
            raise RuntimeError('Forbidden to save object without id!')

        # Reset object to default rotation
        self.rotateObject(-self.rotation)

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

    def updateImageOffsets(self):
        for im in self.data['images']:
            im['x'] = self.sprites[im['path']].x
            im['y'] = self.sprites[im['path']].y

    def updateImageList(self):
        new_dict = {}

        for i, im in enumerate(self['images']):
            sprite = self.sprites.pop(im['path'])
            im['path'] = f'images/{i}.png'
            new_dict[im['path']] = sprite

        self.sprites = new_dict

    def setSpriteFromIndex(self, sprite_in: spr.Sprite, sprite_index: int):
        self.sprites[self.data['images'][sprite_index]
                     ['path']].setFromSprite(sprite_in)


###### Small scenery subclass ######


class SmallScenery(RCTObject):
    def __init__(self, data: dict, sprites: dict, old_id=None):
        super().__init__(data, sprites, old_id)
        if data:
            if data['objectType'] != 'scenery_small':
                raise TypeError("Object is not small scenery.")

            self.object_type = cts.Type.SMALL
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

    def show(self, rotation=None, animation_frame: int = 0, wither: int = 0, glass: bool = True):
        """Still need to implement all possible animation cases and glass objects."""

        if self.subtype == self.Subtype.GLASS and glass:
            if isinstance(rotation, int):
                rotation = rotation % 4
            else:
                rotation = self.rotation

            sprite_index = rotation
            mask_index = rotation+4
            sprite = self.sprites[self.data['images'][sprite_index]['path']]
            mask = self.sprites[self.data['images'][mask_index]['path']]

            color_remap = self.current_first_remap if self.current_first_remap != 'NoColor' else '1st Remap'
            image_paste = spr.colorAllInRemap(
                sprite.show('NoColor', self.current_second_remap,
                            self.current_third_remap),
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

            canvas.paste(s2.show('NoColor', self.current_second_remap, self.current_third_remap),
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

            canvas.paste(s1.show(self.current_first_remap, self.current_second_remap, self.current_third_remap),
                         (s1.x+canvas_size_x, s1.y+canvas_size_y), mask=s1.image)
            canvas.paste(s2.show(self.current_first_remap, self.current_second_remap, self.current_third_remap),
                         (s2.x+canvas_size_x, s2.y+canvas_size_y), mask=s2.image)

            if self.animation_type == self.AnimationType.FOUNTAIN4:

                canvas.paste(s3.show(self.current_first_remap, self.current_second_remap, self.current_third_remap),
                             (s3.x+canvas_size_x, s3.y+canvas_size_y), mask=s3.image)
                canvas.paste(s4.show(self.current_first_remap, self.current_second_remap, self.current_third_remap),
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
                self.current_first_remap, self.current_second_remap, self.current_third_remap), sprite.x, sprite.y

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

    def rotateObject(self, rot=None):
        if not isinstance(rot, int):
            self.rotation = (self.rotation + 1) % 4
        else:
            self.rotation = rot % 4

    def cycleSpritesRotation(self, step: int = 1):
        for i in range(int(len(self.data['images'])/4)):
            image_list = self.data['images'][4*i:4*i+4]
            self.data['images'][4*i:4*i+4] = image_list[-step:] + \
                image_list[:-step]

        self.updateImageList()

    def changeFlag(self, flag, value):
        self.data['properties'][flag] = value

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
            self.data['properties'].pop('frameOffsets')
            self.data['properties'].pop('animationDelay')
            self.data['properties'].pop('animationMask')
            self.data['properties'].pop('numFrames')
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
        shift += 2 if self.animation_type == self.AnimationType.FOUNTAIN4 else 0
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

            self.object_type = cts.Type.LARGE

            self.num_tiles = len(self.data['properties']['tiles'])

            if data['properties'].get('3dFont', False):
                self.subtype = self.Subtype.SIGN
                self.font = self.data['properties']['3dFont']
                self.glyphs = self.font['glyphs']
                self.num_glyph_sprites = self.font['numImages'] * \
                    2*(2-int(self.font.get('isVertical', 0)))

            else:
                self.subtype = self.Subtype.SIMPLE
                self.num_glyph_sprites = 0

        self.rotation_matrices = [
            np.array([[1, 0], [0, 1]]),      # R^0
            np.array([[0, 1], [-1, 0]]),  # R
            np.array([[-1, 0], [0, -1]]),  # R^2
            np.array([[0, -1], [1, 0]])   # R^3
        ]

    def size(self):
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
        x_size, y_size, z_size = self.size()
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
            y_base = y_baseline + \
                int(tile['x']/2) + int(tile['y']/2) - tile.get('z', 0)
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
            raise NotImplementedError(
                "Creating thumbnails is not supported yet for 3d sign objects.")

    # Override base class
    def updateImageOffsets(self):
        for i, im in enumerate(self.data['images']):
            # Update the non-preview sprites
            if i > 3:
                im['x'] = self.sprites[im['path']].x
                im['y'] = self.sprites[im['path']].y
            # preview sprites have different offsets
            else:
                image = self.sprites[im['path']].show()
                im['x'] = -int(image.size[0]/2)
                im['y'] = image.size[1]

    # for now we override this method to do nothing
    def updateImageList(self):
        return

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
   # elif obj_type == 'scenery_large':
   #     return LargeScenery(obj.data, obj.sprites, obj.old_id)
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
   # elif obj_type == 'scenery_large':
   #     return LargeScenery(obj.data, obj.sprites, obj.old_id)
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


def newEmpty(object_type: cts.Type):
    """Instantiates a new empty object of given type."""

    data = {}

    if object_type == cts.Type.SMALL:
        data = copy.deepcopy(cts.data_template_small)
    elif object_type == cts.Type.LARGE:
        data = copy.deepcopy(cts.data_template_large)
    else:
        raise NotImplementedError(
            f"Object type {object_type.value} unsupported by now.")

    sprites = {im['path']: spr.Sprite(None) for im in data['images']}

    return new(data, sprites)
