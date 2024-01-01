# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2023 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from enum import Enum

class Type(Enum):
    SMALL = 'scenery_small'
    LARGE = 'scenery_large'
    WALL = "scenery_wall"
    BANNER = "footpath_banner"
    PATH = "footpath"
    PATHITEM = "footpath_item"
    GROUP = "scenery_group"
    ENTRANCE = "park_entrance"
    PALETTE =  "water"
    TEXT = "scenario text"
    

cursors = [
     "CURSOR_ARROW",
     "CURSOR_BLANK",
     "CURSOR_UP_ARROW",
     "CURSOR_UP_DOWN_ARROW",
     "CURSOR_HAND_POINT",
     "CURSOR_ZZZ",
     "CURSOR_DIAGONAL_ARROWS",
     "CURSOR_PICKER",
     "CURSOR_TREE_DOWN",
     "CURSOR_FOUNTAIN_DOWN",
     "CURSOR_STATUE_DOWN",
     "CURSOR_BENCH_DOWN",
     "CURSOR_CROSS_HAIR",
     "CURSOR_BIN_DOWN",
     "CURSOR_LAMPPOST_DOWN",
     "CURSOR_FENCE_DOWN",
     "CURSOR_FLOWER_DOWN",
     "CURSOR_PATH_DOWN",
     "CURSOR_DIG_DOWN",
     "CURSOR_WATER_DOWN",
     "CURSOR_HOUSE_DOWN",
     "CURSOR_VOLCANO_DOWN",
     "CURSOR_WALK_DOWN",
     "CURSOR_PAINT_DOWN",
     "CURSOR_ENTRANCE_DOWN",
     "CURSOR_HAND_OPEN",
     "CURSOR_HAND_CLOSED"
]

languages = {
    "en-GB": 'English',
    "en-US": 'American English',
    "fr-FR": 'French',
    "de-DE": 'German',
    "es-ES": 'Spanish',
    "it-IT": 'Italian',
    "nl-NL": 'Dutch',
    "sv-SE": 'Swedish',
    "ja-JP": 'Japanese',
    "ko-KR": 'Korean',
    "zh-CN": 'Chinese',
    "zh-TW": 'Taiwanese',
    "pl-PL": 'Polish',
    "pt-BR": 'Portugese',
    "cs-CZ": 'Czech',
    "ru-RU": 'Russian',
    "eo-ZZ": 'Esperanto'
}



# Name: (Byte-Position,Bit)
Jsmall_flags = {

    'SMALL_SCENERY_FLAG_VOFFSET_CENTRE': (6, 0x02),

    'requiresFlatSurface': (6, 0x04),

    'isRotatable': (6, 0x08),

    'isAnimated': (6, 0x10),

    'canWither': (6, 0x20),

    'canBeWatered': (6, 0x40),

    'hasOverlayImage': (6, 0x80),

    'hasGlass': (7, 0x02),

    'hasPrimaryColour': (7, 0x04),

    'SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1': (7, 0x08),

    'SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4': (7, 0x10),

    'isClock': (7, 0x20),

    'SMALL_SCENERY_FLAG_SWAMP_GOO': (7, 0x40),

    'SMALL_SCENERY_FLAG17': (8, 0x01),

    'isStackable': (8, 0x02),

    'prohibitWalls': (8, 0x04),

    'hasSecondaryColour': (8, 0x08),

    'hasNoSupports': (8, 0x10),

    'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED': (8, 0x20),

    'SMALL_SCENERY_FLAG_COG': (8, 0x40),

    'allowSupportsAbove': (8, 0x80),

    'supportsHavePrimaryColour': (9, 0x04),

    'SMALL_SCENERY_FLAG27': (9, 0x08)
}

Jlarge_flags = {

    'hasPrimaryColour': (7, 0x01),

    'hasSecondaryColour': (7, 0x02),

    '3dSign': (7, 0x04),

    'isAnimated': (7, 0x08),

    'isPhotogenic': (7, 0x10)
}


data_template_small = {
  "id": "",
  "authors": "",
  "sourceGame": "custom",
  "objectType": "scenery_small",
  "properties": {
      "height": 0
      },
  "images": [
    {
      "path": "images/00.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/01.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/02.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/03.png",
      "x": 0,
      "y": 0
    }
  ],
  "strings": {
    "name": {
      "en-GB": ""
    }
  }
}

data_template_large =    {
  "id": "",
  "authors": "",
  "sourceGame": "custom",
  "objectType": "scenery_large",
  "properties": { "tiles": [
        {
          "x": 0,
          "y": 0,
          "clearance": 1
        }        ]},
  "images": [
    {
      "path": "images/00.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/01.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/02.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/03.png",
      "x": 0,
      "y": 0
    },
    {
      "path": "images/04.png",
      "x": 0,
      "y": 0
    }
  ],
  "strings": {
    "name": {
      "en-GB": ""
    }
  }
}
