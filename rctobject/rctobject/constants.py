# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 12:41:04 2022

@author: puvlh
"""

cursors = [
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
    "pt-BR": 'Portugese'
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
