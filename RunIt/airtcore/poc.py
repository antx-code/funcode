import ddddocr
import cv2
from loguru import logger
import numpy as np
import asyncio
from init import config
import easyocr
from poker_cards import *
from cols import get_color
from hsv_cv import *

# reader = easyocr.Reader(['ch_sim','en'])
reader = easyocr.Reader(['en'])

CONF = config['COLOR']

async def easyocr_poker(filename):
    result = reader.readtext(filename, detail=0)
    # print(result)
    if not result:
        # print('easyocr: None')
        return None
    result = result[0].upper()
    if result not in POKER_SCOPE:
        # print('easyocr: None')
        return None
    # print(f'easyocr: {result}')
    return result

async def ocr_poker(filename):
    ocr = ddddocr.DdddOcr()
    with open(filename, 'rb') as f:
        image_bytes = f.read()
    res = ocr.classification(image_bytes)
    # print(res)
    result = res.upper()
    if 'I' in result:
        result = result.replace('I', '1')
    if 'O' in result:
        result = result.replace('O', '0')
    if 'o' in result:
        result = result.replace('o', '0')
    if not result:
        # print('ddddocr: None')
        return None
    for chr in result:
        if chr in POKER_SCOPE:
            result = chr
    # print(f'ddddocr: {result}')
    return result

def color_poker(filename):
    try:
        frame = cv2.imread(filename)
        color = get_color(frame)
        print(f'color: {color}')
        return color
    except Exception as e:
        print('color: None')
        return None

async def pokerocr(filename):
    num1 = await ocr_poker(filename)
    num2 = await easyocr_poker(filename)
    if num1 == num2:
        num = num1
    else:
        if num1 and not num2:
            num = num1
        else:
            num = num2
    return num

def pokercolor(filename):
    color1 = color_poker(filename)
    color2 = poker_max_color(filename)
    if color1 == color2:
        color = color1
    else:
        color_keys = get_color_key(filename)
        if len(color_keys):
            color = color2
        elif color1 in color_keys:
            color = color1
    pass

async def poker_num(filename):
    num = await pokerocr(filename)  # 牌面识别
    print(f'num: {num}')
    if not num:
        return None
    # color = color_poker(filename)       # 颜色识别
    color = await poker_max_color(filename)
    print(f'color: {color}')
    try:
        if color == 'blue':
            record = Blue[num]
        elif color == 'red':
            record = Red[num]
        elif color == 'green':
            record = Green[num]
        elif color == 'black':
            record = Black[num]
        else:
            record = None
    except Exception as e:
        record = None
    print(f'********** poker number: {record} **********')
    return record

def poker_dia(filename):
    joker = is_joker(filename)
    num = poker_num(filename)
    if not joker:
        return num
    return joker

if __name__ == '__main__':
    f1 = '/Users/antx/Code/tmp/airt/joker2.png'
    # num = poker_num(f1)
    r = poker_dia(f1)
    print(r)
