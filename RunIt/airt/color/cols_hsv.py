import cv2
import numpy as np
from color.colorList import getColorList

def get_color_count(filename):            # 获取图片颜色
    Img = cv2.imread(filename)                  # 读入一幅图像
    color_count_result = {
        'blue': 0,
        'black': 0,
        'red': 0,
        'green': 0
    }
    kernel_2 = np.ones((2, 2), np.uint8)        # 2x2的卷积核
    kernel_3 = np.ones((3, 3), np.uint8)        # 3x3的卷积核
    kernel_4 = np.ones((4, 4), np.uint8)        # 4x4的卷积核

    if Img is not None:  # 判断图片是否读入
        HSV = cv2.cvtColor(Img, cv2.COLOR_BGR2HSV)  # 把BGR图像转换为HSV格式
        color_dict = getColorList()
        for d in color_dict:
            # mask是把HSV图片中在颜色范围内的区域变成白色，其他区域变成黑色
            mask = cv2.inRange(HSV, color_dict[d][0], color_dict[d][1])

            # 下面四行是用卷积进行滤波
            # erode()函数可以对输入图像用特定结构元素进行腐蚀操作，该结构元素确定腐蚀操作过程中的邻域的形状，
            # 各点像素值将被替换为对应邻域上的最小值：
            erosion = cv2.erode(mask, kernel_3, iterations=1)
            erosion = cv2.erode(erosion, kernel_3, iterations=1)
            # dilate()函数可以对输入图像用特定结构元素进行膨胀操作，该结构元素确定膨胀操作过程中的邻域的形状，
            # 各点像素值将被替换为对应邻域上的最大值：
            dilation = cv2.dilate(erosion, kernel_3, iterations=1)
            dilation = cv2.dilate(dilation, kernel_3, iterations=1)

            # target是把原图中的非目标颜色区域去掉剩下的图像
            target = cv2.bitwise_and(Img, Img, mask=dilation)

            # 将滤波后的图像变成二值图像放在binary中
            ret, binary = cv2.threshold(dilation, 127, 255, cv2.THRESH_BINARY)

            # 在binary中发现轮廓，轮廓按照面积从小到大排列
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            p = 0
            for i in contours:  # 遍历所有的轮廓
                x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
                # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                cv2.rectangle(Img, (x, y), (x + w, y + h), (0, 255,), 3)
                # 给识别对象写上标号
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(Img, str(p), (x - 10, y + 10), font, 1, (0, 0, 255), 2)  # 加减10是调整字符位置
                p += 1

            # print(d, p, '个')  # 终端输出目标数量
            if d == 'blue' or d == 'cyan':
                color_count_result['blue'] += p
            if d == 'red' or d == 'red2':
                color_count_result['red'] += p
            if d == 'black':
                color_count_result['black'] += p
            if d == 'green':
                color_count_result['green'] += p
        return color_count_result

def poker_max_color(filename):            # 获取颜色值最大的颜色
    color_count_dict = get_color_count(filename)
    max_color = list(color_count_dict.keys())[list(color_count_dict.values()).index(max(color_count_dict.values()))]
    return max_color

def get_max_color_key(filename):          # 获取值不为0的颜色
    color_keys = []
    color_count_dict = get_color_count(filename)
    for inx, (k, v) in enumerate(color_count_dict.items()):
        if not v:
            continue
        color_keys.append(k)
    return color_keys

if __name__ == '__main__':
    filename = '/pics/playing/3534616464566779904/PLAYER1/TAIL/1.png'
    # color_count = get_color_count(filename)
    # print(color_count)
    # print(poker_max_color(filename))
