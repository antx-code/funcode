import cv2
import numpy as np
import colorList

# 处理图片
def get_color(frame):
    # print('go in get_color')
    colo_p = 'pics/colo/'
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    maxsum = -100
    color = None
    color_dict = colorList.getColorList()
    for d in color_dict:
        mask = cv2.inRange(hsv, color_dict[d][0], color_dict[d][1])
        cv2.imwrite(colo_p + d + '.png', mask)
        binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        binary = cv2.dilate(binary, None, iterations=2)
        cnts, hiera = cv2.findContours(binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sum = 0
        for c in cnts:
            sum += cv2.contourArea(c)
        if sum > maxsum:
            maxsum = sum
            color = d
    if color == 'cyan':
        color = 'blue'
    if color == 'red2':
        color = 'red'
    return color

if __name__ == '__main__':
    filename = '/Users/antx/Code/tmp/airt/pics/playing/3534305374637129728/LOCAL/TAIL/3.png'
    frame = cv2.imread(filename)
    print(get_color(frame))
