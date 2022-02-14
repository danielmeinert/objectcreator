"""
Module for handling base classes of RCT objects.
Includes file handling (save/open) functions.

Objects may be loaded with from_parkobj and from_dat functions.

JSON data may be accessed and edited as dictionary key: obj[key]

TODO: Loading object from .DAT files

Created 09/26/2021; 16:58:33
@author: Drew
"""

from json import load, dump
from os import mkdir, replace
from PIL import Image
from shutil import unpack_archive, make_archive, move, rmtree
from tempfile import TemporaryDirectory
import numpy as np
from numpy.linalg import matrix_power

class RCTObject:
    """Base class for all editable objects; loads from .parkobj or .DAT files."""

    def __init__(self, data: dict, images: dict):
        """Instantiate object directly given JSON and image data."""
        self.data = data
        self.images = images
        self.rotation = 0
        if data:
            self.tile_size = self.setTileSize()

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
            images = {im['path']: Image.open(f'{temp}/{im["path"]}').convert('RGBA') for im in data['images']}
        return cls(data=data, images=images)

    # @classmethod
    # def from_dat(cls, path: str):
    #     """TODO: Instantiates a new object from a .DAT file."""
    #     raise NotImplementedError

    def save(self, path: str, no_zip : bool = False):
        """Saves an object as .parkobj file to specified path."""
        
        # Bring object in default rotation
        self.rotateObject(-self.rotation)

        
        filename = path + '/' + self.data['id']
        with TemporaryDirectory() as temp:
            with open(f'{temp}/object.json', mode='w') as file:
                dump(obj=self.data, fp=file,indent=2)
            mkdir(f'{temp}/images')
            for name, image in self.images.items():
                image.save(f'{temp}/{name}')
            make_archive(base_name=f'{filename}', root_dir=temp, format='zip')
            replace(f'{filename}.zip', f'{filename}.parkobj')
            if no_zip:
                rmtree(filename, ignore_errors=True)
                mkdir(filename)
               #mkdir(f'{filename}/images')
                move(f'{temp}/images', f'{filename}')
                move(f'{temp}/object.json', filename)

    
    
    def numTiles(self):     
        if self.data['objectType'] != 'scenery_large':
            return 1
        else:
            return len(self.data['properties']['tiles'])

    def setTileSize(self):
        if self.data['objectType'] != 'scenery_large':
            return (1,1, self.data['properties']['height']*8)
        
        max_x=0
        max_y=0
        max_z = 0
        for tile in self.data['properties']['tiles']:
            max_x = max(tile['x'],max_x)
            max_y = max(tile['y'],max_y)
            max_z = max(tile.get('z', 0) +tile['clearance'],max_z)
        
        x = (max_x + 32)/32
        y = (max_y + 32)/32
        z = max_z / 8
        
        return (int(x),int(y),int(z))
    
    def spriteBoundingBox(self, view :int = None):
        if view == None:
            view = self.rotation
        
        if self.data['objectType'] != 'scenery_large':
            return list(self.images.values())[view].size()
        
        x,y,z = self.tile_size

        height = -1 + x*16 + y*16 + z*8
        width  = x*32 + y*32        
        
        return (width,height)
    
    def showSprite(self):
        if self.numTiles() == 1:
            return self.images[list(self.images)[self.rotation]]
        
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
                
                sprite_index = 4+ 4*tile_index+view
                sprite = self.images[list(self.images)[sprite_index]]
                x = self.data['images'][sprite_index]['x']
                y = self.data['images'][sprite_index]['y']
                canvas.paste(sprite,(x_base+x,y_base+y),sprite)
                
            
        
        return canvas.crop(canvas.getbbox())   
    
    def rotateObject(self, rot : int = 1):
        self.rotation = (self.rotation + rot) %4
        if self.numTiles() == 1:
            return
        
        rot_mat = matrix_power(np.array([[0,1],[-1,0]]),rot % 4)
    
        for tile in self.data['properties']['tiles']:
            pos = np.array([tile['x'],tile['y']])
            
            pos = rot_mat.dot(pos)
            tile['x'], tile['y'] = int(pos[0]) , int(pos[1])
        
        
    def getDrawingOrder(self):
        
        tile_index = 0
        order = {}
        
        for tile in self.data['properties']['tiles']:
            score = tile['x'] +tile['y']
            order[tile_index] = score
            tile_index += 1
            
        return sorted(order, key=order.get)
        
        
        



