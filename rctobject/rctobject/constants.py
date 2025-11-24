# -*- coding: utf-8 -*-
"""
*****************************************************************************
 * Copyright (c) 2025 Tolsimir
 *
 * The program "Object Creator" and all subsequent modules are licensed
 * under the GNU General Public License version 3.
 *****************************************************************************
"""

from enum import Enum

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

cursors_data = {
    "CURSOR_UP_ARROW": "                X               "
        "               X.X              "
        "              X...X             "
        "             X.....X            "
        "            X.......X           "
        "           X.........X          "
        "           XXXX...XXXX          "
        "              X...X             "
        "              X...X             "
        "              X...X             "
        "              X...X             "
        "              X...X             "
        "              XXXXX             "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                ",
    "CURSOR_BLANK": ' ' * 32 * 32,    
    "CURSOR_UP_DOWN_ARROW": 
        "                                "
        "                X               "
        "               X.X              "
        "              X.X.X             "
        "             X.X X.X            "
        "            X.X   X.X           "
        "           X.XXX XXX.X          "
        "          X....X X....X         "
        "           XXX.XXX.XXX          "
        "             X.....X            "
        "              XXXXX             "
        "                                "
        "                                "
        "                X               "
        "               X.X              "
        "              X...X             "
        "               X.X              "
        "                X               "
        "                                "
        "                                "
        "              XXXXX             "
        "             X.....X            "
        "             X.XXX.X            "
        "           XXX.X X.XXX          "
        "          X....X X....X         "
        "           X.XXX XXX.X          "
        "            X.X   X.X           "
        "             X.X X.X            "
        "              X.X.X             "
        "               X.X              "
        "                X               "
        "                                "
    ,
    "CURSOR_ZZZ": 
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                           XXX  "
        "                      XXXXX...X "
        "                XXXXXX....XX.X  "
        "               X.....XXX.XX...X "
        "          XXXXXXXXX.X X.XX XXX  "
        "         X......XX.X X....X     "
        "          XXXX.XX.XXX XXXX      "
        "  XXXXXXXX  X.XX.....X          "
        " X........XX.X  XXXXX           "
        " X........X.XXXX                "
        "  XXXX...X......X               "
        "    X...X XXXXXX                "
        "   X...X                        "
        "  X...XXXX                      "
        " X........X                     "
        " X........X                     "
        "  XXXXXXXX                      "
        "                                "
        "                                "
        "                                "
        "                                "
    ,
    "CURSOR_DIAGONAL_ARROWS": 
        ".......                         "
        ".XXXX.                          "
        ".XXX.                           "
        ".XXX.                           "
        ".X..X.                          "
        "..  .X.                         "
        ".    .X.                        "
        "      .X.                       "
        "       .X.    .                 "
        "        .X.  ..                 "
        "         .X..X.                 "
        "          .XXX.                 "
        "          .XXX.                 "
        "         .XXXX.                 "
        "        .......                 "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
    ,
    "CURSOR_PICKER": 
        "             XXXXX              "
        "            X....XX             "
        "           X..XX..XX            "
        "           X.XXXX.XX            "
        "           X.XXXX.XX            "
        "           X..XX..XX            "
        "            X....XX             "
        "            XXXXXXX             "
        "            XXXXXXX             "
        "           X.XXX..XX            "
        "           X..X...XX            "
        "          X....X...XX           "
        "          X...XX...XX           "
        "         X...X  X...XX          "
        "         X...X  X...XX          "
        "        X...X    X...XX         "
        "        X..X      X..XX         "
        "       X...X      X...XX        "
        "       X..X        X..XX        "
        "      X..X          X..XX       "
        "      X..X          X..XX       "
        "     X..X            X..XX      "
        "     X..X            X..XX      "
        "     X..X            X..XX      "
        "     X..X            X..XX      "
        "     X..X            X..XX      "
        "     X...X          X...XX      "
        "      X..X          X..XX       "
        "       X..X        X..XX        "
        "        X..X      X..XX         "
        "         XX.X    X.XXX          "
        "           XXX  XXXX            "
    ,
    "CURSOR_TREE_DOWN": 
        "                                "
        "                 XXX            "
        "               XX...X  XXX      "
        "              X......XX...X     "
        "             XXX...........XX   "
        "             XXX.X...........X  "
        "              XXX............X  "
        "               XXX............X "
        "              XXX.....X.......X "
        "              XXXX.X.........X  "
        "             XXXXXXXX..X....X   "
        "            XXXX.XX.XXX......X  "
        "            XXX.X.XXX...X.....X "
        "            XXXX.X...X....X...X "
        "            XXXXX.X.X....X...XX "
        "            XXXXXXXXXX.....X.XX "
        "             XXXXXX.XXX.X...XX  "
        "    XXXXX      XXXXXXXXXXX.XX   "
        "    X...X        XXXXX.XXXXX    "
        "    X...X         XXX.X         "
        "    X...X          XX.X         "
        "    X...X          XX.X         "
        "    X...X          X..X         "
        "    X...X          X..X         "
        "    X...X          X...X        "
        "XXXXX...XXXXX    XX.....X       "
        " X.........X   XX........XX     "
        "  X.......X   X.....X..XX..X    "
        "   X.....X     XXX.X X.X XX     "
        "    X...X         X   X         "
        "     X.X                        "
        "      X                         "
    ,
    "CURSOR_FOUNTAIN_DOWN": 
        "               .     .          "
        "           .       .    .      ."
        "                 .     .   . .  "
        "             . .    .     .     "
        "                  .   . .      ."
        "                .   .      .    "
        "                   .     .      "
        "                      .         "
        "                    .   .       "
        "                      .         "
        "                     X          "
        "                    XXX         "
        "                    X.X         "
        "                 XXXX.XXXX      "
        "               XX...X.XX..XX    "
        "              X....X.XXXXX..X   "
        "              X.....XXXXX...X   "
        "    XXXXX     XXX.........XXX   "
        "    X...X     X..XXXXXXXXX.XX   "
        "    X...X      X.......XXXXX    "
        "    X...X       XXX...XXXXX     "
        "    X...X         XXXXXXX       "
        "    X...X          X.XXX        "
        "    X...X          X..XX        "
        "    X...X          X..XX        "
        "XXXXX...XXXXX     X..XXXX       "
        " X.........X     X..XXX.XX      "
        "  X.......X     X.......XXX     "
        "   X.....X      XX.....XX.X     "
        "    X...X        XXXXXXXXX      "
        "     X.X           XXXXX        "
        "      X                         "
    ,
    "CURSOR_STATUE_DOWN": 
        "                                "
        "                                "
        "             X             X    "
        "             XXX      XX  XX    "
        "              X.X    X..X  XX   "
        "               X.X   X..X  XX   "
        "                X.XX X.XX X.X   "
        "                 X..X.X XX.X    "
        "                  X....X..X     "
        "                  X......X      "
        "                   X....X       "
        "                   X....X       "
        "                    X..X        "
        "                    X...X       "
        "                    X...X       "
        "                     X.X        "
        "                     X.X        "
        "    XXXXX           X...X       "
        "    X...X            X..X       "
        "    X...X            X.X        "
        "    X...X           XX.X        "
        "    X...X           X..X        "
        "    X...X         XXXXXXX       "
        "    X...X         X.....X       "
        "    X...X         X.....X       "
        "XXXXX...XXXXX     X.....X       "
        " X.........X      X.....X       "
        "  X.......X       X.....X       "
        "   X.....X       XXXXXXXXX      "
        "    X...X       X.........X     "
        "     X.X        XXXXXXXXXXX     "
        "      X                         "
    ,
    "CURSOR_BENCH_DOWN": 
        "                                "
        "                                "
        "             XX                 "
        "             X.XX               "
        "             X...XX             "
        "             X.....XX           "
        "             XX......XX         "
        "             X.XX......XX       "
        "             X.X XX......XX     "
        "            XX.X   XX......XX   "
        "          XX..XX     XX......X  "
        "        XX......XX     XX....X  "
        "        XXXX......XX     XX..X  "
        "        X.X XX......XX     XXX  "
        "        X.X  XXX......XX   X.X  "
        "         X      XX......XX X.X  "
        "                XXXX......XX.X  "
        "    XXXXX       X.X XX......XX  "
        "    X...X       X.X   XX..XXXX  "
        "    X...X        X     XXX X.X  "
        "    X...X              XXX X.X  "
        "    X...X              X.X  X   "
        "    X...X              X.X      "
        "    X...X               X       "
        "    X...X                       "
        "XXXXX...XXXXX                   "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         "
    ,
    "CURSOR_CROSS_HAIR": 
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "              X                 "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "              X                 "
        "                                "
        "    XXXXXXX   X   XXXXXXX       "
        "   X.......X X.X X.......X      "
        "    XXXXXXX   X   XXXXXXX       "
        "                                "
        "              X                 "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "             X.X                "
        "              X                 "
        "                                "
        "                                "
        "                                "
        "                                "
    ,
    "CURSOR_BIN_DOWN": 
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                   XXX          "
        "                  X   X         "
        "                  XXXXX         "
        "                XX....XXX       "
        "               X........XX      "
        "              X..X.X.XXXXXX     "
        "              X..........XX     "
        "              XXXXXXXXXXXXX     "
        "               X.......XXX      "
        "               X.X......XX      "
        "               X.X.X....XX      "
        "    XXXXX      X.X.X.....X      "
        "    X...X      X.X.X...X.X      "
        "    X...X      X.X.X...X.X      "
        "    X...X      X.X.X.X.X.X      "
        "    X...X      X.X.X.X.X.X      "
        "    X...X      X.X.X.X.X.X      "
        "    X...X      X.X.X.X.X.X      "
        "    X...X      X.X.X.X.X.X      "
        "XXXXX...XXXXX  X.X.X.X.X.X      "
        " X.........X   X.X.X.X.X.X      "
        "  X.......X    XXXXXXXXXXX      "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         "
    ,
    "CURSOR_LAMPPOST_DOWN": 
        "                   XXX          "
        "                  X...X         "
        "                 X.....X        "
        "                XXXXXXXXX       "
        "                 XXXX..X        "
        "                 XX....X        "
        "                 XX....X        "
        "                  XX..X         "
        "                  XXXXX         "
        "                   XXX          "
        "                   X.X          "
        "                X  X.X  X       "
        "               XXXXX.XXXXX      "
        "                X  X.X  X       "
        "                   X.X          "
        "                   X.X          "
        "                   X.X          "
        "    XXXXX          X.X          "
        "    X...X          X.X          "
        "    X...X          X.X          "
        "    X...X          X.X          "
        "    X...X          X.X          "
        "    X...X          X.X          "
        "    X...X          XXX          "
        "    X...X          XXX          "
        "XXXXX...XXXXX     XX..X         "
        " X.........X     XX....X        "
        "  X.......X      XX....X        "
        "   X.....X       XXX...X        "
        "    X...X        XXXXX.X        "
        "     X.X        XXXXXXXXX       "
        "      X                         "
    ,
    "CURSOR_FENCE_DOWN": 
        "                                "
        "   XX                           "
        "  X.XX                          "
        " X..XXX  XX                     "
        " X....XXX.XX                    "
        "  X.....X.XX   XX               "
        "  X.XX....XXX X.XX              "
        "  X.XXXX....XXX.XX   XX         "
        "  X.XX  X.....X.XX  X.XX        "
        "  X.XX  X.XX.....XX X.XX   XX   "
        " XX.XX  X.XXXX.....XX.XX  X.XX  "
        " XXXXX  X.XX  X.X.....XX  X.XX  "
        "   XXXX X.XX  X.XXX....XX X.XX  "
        "     XXXX.XX  X.XX XX....XX.XX  "
        "       XXXXX  X.XX  X.X.....XX  "
        "         XXXX X.XX  X.XXX....XX "
        "           XXXX.XX  X.XX XX..XX "
        "    XXXXX    XXXXX  X.XX  X.XXX "
        "    X...X      XXXX X.XX  X.XX  "
        "    X...X        XXXX.XX  X.XX  "
        "    X...X          XXXXX  X.XX  "
        "    X...X            XXXX X.XX  "
        "    X...X              XXXX.XX  "
        "    X...X                XXXX   "
        "    X...X                  XX   "
        "XXXXX...XXXXX                   "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         "
    ,
    "CURSOR_FLOWER_DOWN": 
        "                   X            "
        "                  X.X           "
        "                 X...X          "
        "           XX    X...X    XX    "
        "          X..X   X.X.X   X..X   "
        "          X...X  X.X.X  X...X   "
        "           X...X X.X.X X...X    "
        "            X.X.X XXX X.X.X     "
        "             X.XX XXX XX.X      "
        "              XXXX...XXXX       "
        "         XXXXX  X..X..X  XXXXX  "
        "        X.....XX.X...XXXX.....X "
        "       X...XXX.XX...X..XXXXX...X"
        "        X.....XX..X...XXX.....X "
        "         XXXXX  X...X.X  XXXXX  "
        "              XXXXX..XXXX       "
        "             X.XX XXX XX.X      "
        "    XXXXX   X.X.X XXX X.X.X     "
        "    X...X  X...X X.X.X X...X    "
        "    X...X  X..X  X.X.X  X..X    "
        "    X...X   XX   X...X   XX XX  "
        "    X...X  XX    X...X    XX..X "
        "    X...X X..XX  X...X   X....X "
        "    X...X X....X  X.X   X.....X "
        "    X...X X.....X XXX  X..X..X  "
        "XXXXX...XXXXX.X.X XXX X..X...X  "
        " X.........X...X.XX.X X.X...X   "
        "  X.......X X...XXX.XX.X...X    "
        "   X.....X   XX..X..X.X..XX     "
        "    X...X      XX......XX       "
        "     X.X         XXXXXX         "
        "      X                         "
    ,
    "CURSOR_PATH_DOWN": 
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "           XX                   "
        "         XX..XX                 "
        "       XX....X.XX               "
        "     XX..X..X....XX             "
        "   XX.X...X..X...X.XX           "
        " XX...X...XXX.X..X...XX         "
        " XXXX..XXX.....X.X...X.XX       "
        "   XXXX...X..XXXXXXXXX...XX     "
        "     XXXX..XX...X.....X..X.XX   "
        "       XXXX.....X.....X..X...XX "
        "         XXXX..X.X...X.X.XXXX..X"
        "           XXXX...X.X...X....XXX"
        "    XXXXX    XXXX..X.X..X..XXXX "
        "    X...X      XXXX...X..XXXX   "
        "    X...X        XXXX..XXXX     "
        "    X...X          XXXXXX       "
        "    X...X            XX         "
        "    X...X                       "
        "    X...X                       "
        "    X...X                       "
        "XXXXX...XXXXX                   "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         ",
    "CURSOR_DIG_DOWN":"                                "
        "                          XX    "
        "                         X..X   "
        "                        X.X..X  "
        "                       X.X X..X "
        "                      X.X   X.XX"
        "                      X.X  X.XX "
        "                      X..XX.XX  "
        "                     X.....XX   "
        "                    X...XXXX    "
        "                   X...XX       "
        "              XX  X.X.X         "
        "             X..XX...XX         "
        "            X..XX...XX          "
        "           X.X.X...XX           "
        "          X...X...XX            "
        "          X..X...XXXX           "
        "    XXXXXX...X.XXXX..X          "
        "    X...XX...XXXXX...X          "
        "    X...XX....XX..X.X           "
        "    X...X X........X            "
        "    X...X  X......X             "
        "    X...X   X...XX              "
        "    X...X    XXX                "
        "    X...X                       "
        "XXXXX...XXXXX                   "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         ",
    "CURSOR_WATER_DOWN": "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "                                "
        "    X     X     X     X         "
        "    X     X     X     X         "
        "   X.X   X.X   X.X   X.X        "
        " XX...XXX...XXX...XXX...XX      "
        "X...X.....X.....X.....X...X     "
        " XXX XXXXX XXXXX XXXXX XXX      "
        "                                "
        "          X     X     X     X   "
        "          X     X     X     X   "
        "         X.X   X.X   X.X   X.X  "
        "        X...XXX...XXX...XXX...X "
        "    XXXXX.X.....X.....X.....X..X"
        "    X...XX XXXXX XXXXX XXXXX XX "
        "    X...X                       "
        "    X...X       X     X         "
        "    X...X       X     X         "
        "    X...X      X.X   X.X        "
        "    X...X    XX...XXX...XX      "
        "XXXXX...XXXXX...X.....X...X     "
        " X.........X XXX XXXXX XXX      "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         ",
    "CURSOR_HOUSE_DOWN": "                                "
        "                                "
        "                   X  XXXXXX    "
        "                  X.X X....X    "
        "                 X...X XXXX     "
        "                X..X..XX..X     "
        "               X...XX..X..X     "
        "              X.....XX....X     "
        "             X...XXXXXX...X     "
        "            X.........XX..X     "
        "           X....XXXXXXXXX..X    "
        "          X.............XX..X   "
        "         X...XXXXXXXXXXXXXX..X  "
        "        XXXX.............XXXXXX "
        "           X...............X    "
        "           X...............X    "
        "           X...XXXX.XXXXXX.X    "
        "           X...X  X.X    X.X    "
        "    XXXXX  X...X  X.X    X.X    "
        "    X...X  X...X  X.X    X.X    "
        "    X...X  X...X  X.XXXXXX.X    "
        "    X...X  X...X  X........X    "
        "    X...X  X...X  X........X    "
        "    X...X  XXXXXXXXXXXXXXXXX    "
        "    X...X                       "
        "XXXXX...XXXXX                   "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         ",
    "CURSOR_VOLCANO_DOWN": "            X   X X             "
        "              X     X           "
        "                 X              "
        "              X  X              "
        "             XXXX XX            "
        "           XXXXXXXXXXX          "
        "           X.XXXX....X          "
        "          XX.......XXXX         "
        "         XXX.XX..XXX..X         "
        "         X.XX.X.X...X..X        "
        "        X......X...XXX..X       "
        "      XX....X.......X.X..XXX    "
        "     X.....XX......X.XXXX...X   "
        "   XX.....XX........X.X.X.X..XX "
        "  X...XXXX....X......XXX.XXXXXXX"
        " XXXXX   X.XXXXXX...XXXXXXX XX  "
        " X      XXXX    XX.XX   XX      "
        "         X        X             "
        "    XXXXX                       "
        "    X...X                       "
        "    X...X                       "
        "    X...X                       "
        "    X...X                       "
        "    X...X                       "
        "    X...X                       "
        "XXXXX...XXXXX                   "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         ",
    "CURSOR_WALK_DOWN":  "                                "
        "      XXX                       "
        "     X...X                      "
        "     X....X                     "
        "      X....X                    "
        "       X...X                    "
        "        XXX  X                  "
        "           XX.X                 "
        "           X..X                 "
        "            XX                  "
        "                                "
        "       XXX         XXX          "
        "      X...X       X...X         "
        "      X....X      X....X        "
        "       X....X      X....X       "
        "        X...X       X...X       "
        "         XXX  X      XXX  X     "
        "            XX.X        XX.X    "
        "    XXXXX   X..X        X..X    "
        "    X...X    XX          XX     "
        "    X...X                       "
        "    X...X           XXX         "
        "    X...X          X...X        "
        "    X...X          X....X       "
        "    X...X           X....X      "
        "XXXXX...XXXXX        X...X      "
        " X.........X          XXX  X    "
        "  X.......X              XX.X   "
        "   X.....X               X..X   "
        "    X...X                 XX    "
        "     X.X                        "
        "      X                         ",
    "CURSOR_PAINT_DOWN":"                                "
        "                           XXX  "
        "                         XXXXXX "
        "                        XXXXX.X "
        "                       XXXXX.XX "
        "                      XXXXX..X  "
        "              XX     XXXXX..XX  "
        "             XXXX    X..X..XX   "
        "            XXXXXX  X....XXX    "
        "           XX.XXXXXXX....XX     "
        "          XXXX.XXXX.....XX      "
        "         XXXXXX.XXX...XX        "
        "        XXXXXXXX.XX...X         "
        "        XX.XXXXXX.XXXXX         "
        "         XXXXXXXXX.XXXXX        "
        "          XX.XXXXXX.XXXXX       "
        "           XX.XXXXXX.XXXXX      "
        "     XXXXX  XXXXXXXXX.XXXX      "
        "     X...X   XX.X..XXX.XXX      "
        "     X...X    XX.....XXXX       "
        "     X...X     XX.....XX        "
        "     X...X      XX...XX         "
        "     X...X       XX.XX          "
        "     X...X        X.X           "
        " XXXXX...XXXXX     X            "
        "  X.........X                   "
        "   X.......X                    "
        "    X.....X                     "
        "     X...X                      "
        "      X.X                       "
        "       X                        "
        "                                ",
    "CURSOR_ENTRANCE_DOWN": "  X                         X   "
        " X.X                       X.X  "
        "X...X                     X...X "
        " X.X                       X.X  "
        " XXXXXXXXXXXXXXXXXXXXXXXXXXXXX  "
        " X.XX.....................XX.X  "
        " X.X X...................X X.X  "
        " X.X X...................X X.X  "
        " X.X X...................X X.X  "
        " X.XXX....................XX.X  "
        " X.XXXXXXXXXXXXXXXXXXXXXXXXX.X  "
        " X.X                       X.X  "
        " X.X                       X.X  "
        " X.X                       X.X  "
        " X.X                       X.X  "
        " X.X                       X.X  "
        " X.X                       X.X  "
        " X.XXXXXX                  X.X  "
        "XX.XX...X                  X.X  "
        " X.XX...X             X X XX.X X"
        " X.XX...X                  X.X  "
        "XX.XX...X                  X.X  "
        " X.XX...X            X X XXX.X  "
        "    X...X                       "
        "    X...X               XX X  X "
        "XXXXX...XXXXX       XXX         "
        " X.........X                    "
        "  X.......X                     "
        "   X.....X                      "
        "    X...X                       "
        "     X.X                        "
        "      X                         ",
    "CURSOR_HAND_OPEN":"             XX    X            "
        "            X..X  XXX           "
        "            X..X  X..X          "
        "      XX    X...X X..X          "
        "     X..X   X...X X..X  XX      "
        "     X...X  X....XX...XX..X     "
        "     X....X  X...XX...XX...X    "
        "     XX...X  X...XX....XX..X    "
        "      X....X X....X....XX..X    "
        "      XX....XX....X....X...X    "
        "       X.....X....X....X...X    "
        "       XX....XX........X...X    "
        "        X.....X.............X   "
        "        XX..................X   "
        "         XX.................X   "
        "          X.................X   "
        "          XX................X   "
        "          XX................X   "
        "           X................X   "
        "           X................X   "
        "           X...............X    "
        "           X...............X    "
        "          X................X    "
        "          X................X    "
        "    XXXXXX.................X    "
        "   X........................X   "
        "   X.X......................X   "
        "   X..X.....................X   "
        "    XXXX....XXXX.............X  "
        "       XXXXXX  XX............X  "
        "                XX.........XX   "
        "                 XXXXXXXXXX     ",
    "CURSOR_HAND_CLOSED": "                                "
        "          XXXX  XXX             "
        "         X....XX...X            "
        "         X.....XX...XX          "
        "          X.....X....XXX        "
        "    XXX   X......X....X.X       "
        "   X...XX  XX....XX...X..X      "
        "   X.....XX XX...XX....X..X     "
        "   XX......X X....X....X..X     "
        "    XX......XX....X....X...X    "
        "     XX......X....X....X...X    "
        "      XX.....XX........X...X    "
        "        X.....X.............X   "
        "        XX..................X   "
        "         XX.................X   "
        "          X.................X   "
        "          XX................X   "
        "          XX................X   "
        "           X................X   "
        "           X................X   "
        "     XXX   X...............X    "
        "    X...X  X...............X    "
        "    X....XX................X    "
        "    X.X....................X    "
        "    X.X....................X    "
        "     X......................X   "
        "     X......................X   "
        "      XXX...................X   "
        "         XXXXXXX.............X  "
        "               XX............X  "
        "                XX.........XX   "
        "                 XXXXXXXXXX     "
}

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

list_small_animation_flags = ['hasOverlayImage',
                              'SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1',
                              'SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4',
                              'isClock',
                              'SMALL_SCENERY_FLAG_SWAMP_GOO',
                              'SMALL_SCENERY_FLAG17',
                              'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED',
                              'SMALL_SCENERY_FLAG_COG']

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
        "height": 0,
        'isRotatable': True
    },
    "images": [
        {
            "path": "images/0.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/1.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/2.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/3.png",
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

data_template_large = {
    "id": "",
    "authors": "",
    "sourceGame": "custom",
    "objectType": "scenery_large",
    "properties": {"tiles": [
        {
          "x": 0,
          "y": 0,
          "z": 0,
          "clearance": 1,
          "walls": 0,
          "corners": 15
        }]},
    "images": [
        {
            "path": "images/0.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/1.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/2.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/3.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/4.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/5.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/6.png",
            "x": 0,
            "y": 0
        },
        {
            "path": "images/7.png",
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


