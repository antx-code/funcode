import ddddocr
import cv2
from loguru import logger
import numpy as np
from init import config

CONF = config['COLOR']

def ocr_poker(filename):
    ocr = ddddocr.DdddOcr()
    with open(filename, 'rb') as f:
        image_bytes = f.read()
    res = ocr.classification(image_bytes)
    print(f'{filename}: {res.upper()}')

def rgb_poker(filename):
    image = cv2.imread(filename)[:,:,::-1]  #直接转化为了RGB
    print(max(image))

def t2(filename):
    # 载入原图
    img_original = cv2.imread(filename)
    # 转变为HSV颜色空间
    img_hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)
    # 返回黄色区域的二值图像
    img_yellow = cv2.inRange(img_original, (27, 160, 215), (83, 255, 255))
    cv2.imshow('img_original', img_original)
    cv2.imshow('img_target', img_yellow)
    cv2.waitKey()
    cv2.destroyAllWindows()


def get_dominant_colors(infile):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.open(infile)

    # 缩小图片，否则计算机压力太大
    small_image = image.resize((80, 80))
    result = small_image.convert(
        "P", palette=Image.ADAPTIVE, colors=10
    )

    # 10个主要颜色的图像

    # 找到主要的颜色
    palette = result.getpalette()
    color_counts = sorted(result.getcolors(), reverse=True)
    colors = list()

    for i in range(10):
        palette_index = color_counts[i][1]
        dominant_color = palette[palette_index * 3: palette_index * 3 + 3]
        colors.append(tuple(dominant_color))

    # print(colors)
    return colors


def dia():
    pass

if __name__ == '__main__':
    filename = '1.png'
    # ocr_poker(filename)
    # rgb_poker(filename)
    # t2(filename)
    r = get_dominant_colors(filename)
    print(r)
