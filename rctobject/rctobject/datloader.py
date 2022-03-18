# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 16:29:36 2022

@author: puvlh
"""
import datloader_data as prop

getCursor = {
    1: "CURSOR_BLANK",
    2: "CURSOR_UP_ARROW",
    3: "CURSOR_UP_DOWN_ARROW",
    4: "CURSOR_HAND_POINT",
    5: "CURSOR_ZZZ",
    6: "CURSOR_DIAGONAL_ARROWS",
    7: "CURSOR_PICKER",
    8: "CURSOR_TREE_DOWN",
    9: "CURSOR_FOUNTAIN_DOWN",
    10: "CURSOR_STATUE_DOWN",
    11: "CURSOR_BENCH_DOWN",
    12: "CURSOR_CROSS_HAIR",
    13: "CURSOR_BIN_DOWN",
    14: "CURSOR_LAMPPOST_DOWN",
    15: "CURSOR_FENCE_DOWN",
    16: "CURSOR_FLOWER_DOWN",
    17: "CURSOR_PATH_DOWN",
    18: "CURSOR_DIG_DOWN",
    19: "CURSOR_WATER_DOWN",
    20: "CURSOR_HOUSE_DOWN",
    21: "CURSOR_VOLCANO_DOWN",
    22: "CURSOR_WALK_DOWN",
    23: "CURSOR_PAINT_DOWN",
    24: "CURSOR_ENTRANCE_DOWN",
    25: "CURSOR_HAND_OPEN",
    26: "CURSOR_HAND_CLOSED"
}

languages = {
    0: "en-GB",
    1: "en-US",
    2: "fr-FR",
    3: "de-DE",
    4: "es-ES",
    5: "it-IT",
    6: "nl-NL",
    7: "sv-SE",
    8: "ja-JP",
    9: "ko-KR",
    10: "zh-CN",
    11: "zh-TW",
    13: "pt-BR"
}


def rle_decode(string: bytes):
    srcLength = len(string)
    output = []
    i = 5
    if i >= srcLength:
        return False

    if string[0] == 0:
        return string[5:]
    if string[0] != 1:
        return False

    while i < srcLength:
        byte = string[i]
        i += 1
        if (byte & 0x80) == 0:
            copy = byte + 1
            if copy + i > srcLength:
                raise RuntimeError('EXCEPTION_MSG_CORRUPT_RLE', copy, byte, i)

            for c in string[i:i + copy]:
                output.append(c)
            i += copy

        else:
            repeat = (~byte & 0xff)+2
            if i + 1 > srcLength:
                raise RuntimeError('EXCEPTION_MSG_CORRUPT_RLE')

            repeated_byte = string[i]
            i += 1

            for j in range(repeat):
                output.append(repeated_byte)

    return bytes(output)


def array_push(arr, flag):
    arr[flag] = True


def get_source(flag):
    val = (flag & 0xf0) >> 4
    if val == 8:
        return 'rct2'
    elif val == 1:
        return 'rct2ww'
    elif val == 2:
        return 'rct2tt'
    else:
        return 'custom'


def get_object_type(flag):
    val = flag & 0x0f
    if val == 0:
        return "ride"

    elif val == 1:
        return "scenery_small"

    elif val == 2:
        return "scenery_large"

    elif val == 3:
        return "scenery_wall"

    elif val == 4:
        return "footpath_banner"

    elif val == 5:
        return "footpath"

    elif val == 6:
        return "footpath_item"

    elif val == 7:
        return "scenery_group"

    elif val == 8:
        return "park_entrance"

    elif val == 9:
        return "water"

    elif val == 10:
        return "scenario text"

    else:
        raise RuntimeError(
            'DAT-file corrupted. Object type cannot be extracted.')


def tag_small_scenery_header(data, tags):
    if(len(data) < 0x1C):
        return RuntimeError('Could not read small scenery header, not correct length.')
    tags['price'] = int.from_bytes(data[12:14], 'little', signed=True)
    tags['removalPrice'] = int.from_bytes(data[14:16], 'little', signed=True)
    tags['cursor'] = getCursor.get(data[11], 'CURSOR_ARROW')
    tags['height'] = data[10]
    tags['shape'] = tag_small_scenery_determine_shape(data)

    for flag, ind in prop.Jsmall_flags.items():
        if ((data[ind[0]] & ind[1]) == ind[1]):
            array_push(tags, flag)

    if tags.get('isAnimated', False):
        tags['animationDelay'] = int.from_bytes(
            data[20:22], 'little', signed=False)
        tags['animationMask'] = int.from_bytes(
            data[22:24], 'little', signed=False)
        tags['numFrames'] = int.from_bytes(data[24:26], 'little', signed=False)


def tag_small_scenery_determine_shape(data):
    # Determine object size
    isFullTile = ((data[6] & 0x1) == 0x1)
    isDiag = ((data[7] & 0x1) == 0x1)
    is3q = ((data[9] & 0x2) == 0x2)
    is2q = ((data[9] & 0x1) == 0x1)

    if isFullTile:
        part0 = "2/4" if is2q else ("3/4" if is3q else "4/4")
    else:
        # TT:ARTDEC29 is only known occurrence of a 2/4 or 3/4 without isFullTile
        part0 = "2/4" if is2q else ("3/4" if is3q else "1/4")
    if isDiag:
        part0 += "+D"

    return part0


def tag_small_scenery_scan_optional(data, tags, pos):
    length = len(data)

    if tags.get('isAnimated', False):
        frames = []
        if pos >= length:
            raise RuntimeError("Error while scanning optional")

        while data[pos] != 0xff:
            frames.append(data[pos])
            pos += 1
            if pos >= length:
                raise RuntimeError("Error while scanning optional")

        tags['framesOffsets'] = frames

    pos += 1
    if pos >= length:
        raise RuntimeError("Error while scanning optional")


def read_string_table(data, pos):

    length = len(data)

    string_table = {}
    while data[pos] != 0xFF:

        if(pos >= length-1):
            return False
        language = languages.get(data[pos], 'skip')
        pos += 1
        name = ''
        while data[pos] != 0:
            name += chr(data[pos])
            pos += 1
            if pos >= length:
                return False

        pos += 1
        if pos >= length:
            return False
        string_table[language] = name

    pos += 1
    return string_table, pos


def read_dat_info(filename: str):
    result = {}
    tags = {}

    with open(filename, "rb") as f:
        header = f.read(16)
        object_flag = header[0]
        name = header[4:12].decode('utf-8')
        checksum = header[12:16].hex().upper()

        result['id'] = ''
        result['authors'] = ''
        result['version'] = '1.0'
        result['SourceGame'] = get_source(object_flag)
        result['originalId'] = f'000000{hex(object_flag)[2:].zfill(2)}|{name}|00000000'

        object_type = get_object_type(object_flag)
        result['objectType'] = object_type
        string = f.read()
        chunk = rle_decode(string)

        pos = 0

        if object_type == 'ride':
            pass

        if object_type == 'scenery_small':
            tag_small_scenery_header(chunk, tags)

            pos += 0x1C
            result['strings'], pos = read_string_table(chunk, pos)
            if result['strings'].get('en-US', False):
                result['strings'].pop('en-US')
            if result['strings'].get('skip', False):
                result['strings'].pop('skip')
            # skip group info
            pos += 16
            tag_small_scenery_scan_optional(chunk, tags, pos)

            # result["image"] = small_scenery_get_preview(chunk, pos)
            #	if(result["image"] == =FALSE)return FALSE

        result['properties'] = tags

        return result

    # 	if object_type == 2:
    # 		if(tag_large_scenery_header(chunk, tags) ===FALSE)return FALSE
    # 	pos += 0x1A
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	//skip group info
    # 	pos += 16
    # 	tile_info = large_scenery_scan_optional(chunk, pos)
    # 		if(tile_info == =FALSE)return FALSE
    # 		if((ord(chunk[7]) & 0x4) != 0x4)
    # 		{
    # 		result["image"] = large_scenery_get_preview(chunk, pos, tile_info)
    # 			if(result["image"] == =FALSE)return FALSE
    # 		}

    # 	if object_type == 3:
    # 		if(tag_wall_header(chunk, tags) ===FALSE)return FALSE
    # 	pos += 0xE
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	//skip group info
    # 	pos += 16
    # 	result["image"] = wall_get_preview(chunk, pos)
    # 		if(result["image"] == =FALSE)return FALSE

    # 	if object_type == 4:
    # 		if(tag_path_banner_header(chunk, tags) ===FALSE)return FALSE
    # 	pos += 0xC
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	//skip group info
    # 	pos += 16
    # 	result["image"] = path_banner_get_preview(chunk, pos)
    # 		if(result["image"] == =FALSE)return FALSE

    # 	if object_type == 5:
    # 	pos += 0xE
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	result["image"] = path_get_preview(chunk, pos)
    # 		if(result["image"] == =FALSE)return FALSE

    # 	if object_type == 6:
    # 		if(tag_path_object_header(chunk, tags) ===FALSE)return FALSE
    # 	pos += 0xE
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	//skip group info
    # 	pos += 16
    # 	result["image"] = path_object_get_preview(chunk, pos)
    # 		if(result["image"] == =FALSE)return FALSE

    # 	if object_type == 7:
    # 	pos += 0x10E
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	result["members"] = scenery_group_scan_optional(chunk, pos)
    # 		if(result["members"] == =FALSE)return FALSE
    # 	result["image"] = read_image(chunk, pos, 0, TRUE)["image"]
    # 		if(result["image"] == =FALSE)return FALSE

    # 	if object_type == 8:
    # 	pos += 0x8
    # 	result["name_table"] = read_string_table(chunk, pos)
    # 		if(result["name_table"] == =FALSE)return FALSE
    # 	result["image"] = park_entrance_get_preview(chunk, pos)
    # 		if(result["image"] == =FALSE)return FALSE
