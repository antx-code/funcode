import asyncio
import uvloop
import time
from poker_cards import *
from comser.funcs import *
from color.cols_hsv import poker_max_color
from pocr.ocrs import poker_ocr, ddddocr_poker
from init import config
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

CONF = config['COLOR']

# async def poker_dia(filename):
#     num = await asyncio.create_task(poker_ocr(filename))                 # 牌面识别
#     print(f'{filename} poker_dia num: {num}')
#     if not num:
#         return None
#     color = await asyncio.create_task(poker_max_color(filename))         # 颜色识别
#     print(f'poker_dia color: {color}')
#     try:
#         if color == 'blue':
#             record = Blue[num]
#         elif color == 'red':
#             record = Red[num]
#         elif color == 'green':
#             record = Green[num]
#         elif color == 'black':
#             record = Black[num]
#         else:
#             record = None
#     except Exception as e:
#         record = None
#     print(f'********** poker number: {record} **********')
#     return record

def poker_dia(filename, task_id, records, record_player, record_dao_poker, inx):
    # num = poker_ocr(filename)                 # 牌面识别


    max_color, color_dict, color_list, no_max_color = poker_max_color(filename)         # 颜色识别
    print(f'before max_color: {max_color}, color_dict: {color_dict}, color_list: {color_list}, no_max_color: {no_max_color}')
    # if max_color == 'black' and no_max_color == 'black' and 'gray' in color_list:
    #     c_b = color_dict.get('blue', 0)
    #     c_r = color_dict.get('red', 0)
    #     c_g = color_dict.get('green', 0)
    #     c_c = color_dict.get('cyan', 0)
    #     if c_c != 0:
    #         c_b = c_b - c_c
    #         c_g = c_g - c_c
    #         b_num = color_dict['black']
    #         if b_num >= max(c_b, c_r, c_g):
    #             max_color = 'black'
    #             no_max_color = 'black'
    #     else:
    #         if max(c_b, c_r, c_g) == c_b:
    #             max_color = 'blue'
    #             no_max_color = 'blue'
    #         elif max(c_b, c_r, c_g) == c_r:
    #             max_color = 'red'
    #             no_max_color = 'red'
    #         else:
    #             max_color = 'green'
    #             no_max_color = 'green'
    print(f'after max_color: {max_color}, color_dict: {color_dict}, color_list: {color_list}, no_max_color: {no_max_color}')

    # if not color_list:
    #     color = max_color
    #     print(f'final color 1: {color}')
    #     try:
    #         num = ddddocr_poker(filename, max_color)
    #         print(f'{filename} poker_dia num: {num}')
    #         if color == 'blue':
    #             record = Blue[num]
    #         elif color == 'red':
    #             record = Red[num]
    #         elif color == 'green':
    #             record = Green[num]
    #         elif color == 'black':
    #             record = Black[num]
    #         else:
    #             record = -1
    #     except Exception as e:
    #         record = -1
    # else:

    num = ddddocr_poker(filename, max_color)
    print(f'{filename} poker_dia num: {num}')
    if num == -1:
        if max_color == 'yellow':
            record = -1
        elif ((max_color == 'gray' or (max_color == 'blue' and 'gray' in color_list))) and (len(color_list) <= 3) and 'yellow' not in color_list:        # 小王
            record = 52
        elif max_color == 'blue':            # 大王
            if 'yellow' in color_list or 'red' in color_list:
                record = 53
            else:
                record = -1
        # elif max_color == 'yellow':
        else:
            record = -1
    elif num == 53:
        record = 53
    else:
        color = no_max_color
        print(f'final color 2: {color}')
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
                record = -1
        except Exception as e:
            record = -1

    # try:
    #     if color == 'blue':
    #         record = Blue[num]
    #     elif color == 'red':
    #         record = Red[num]
    #     elif color == 'green':
    #         record = Green[num]
    #     elif color == 'black':
    #         record = Black[num]
    #     else:
    #         record = None
    # except Exception as e:
    #     record = None
    print(f'********** poker number: {record} **********')

    # 测试时注销，生产时打开
    print(f'records[{record_player}][{record_dao_poker}][{inx}]: {records[record_player][record_dao_poker][inx]}')

    # if record == -1 and records[record_player][record_dao_poker][inx] != -1:
    #     pass
    # else:

    if records[record_player][record_dao_poker][inx] == -1 and record != -1:
        records[record_player][record_dao_poker][inx] = record

        # set_living_status_redis(task_id, {'records': records})

if __name__ == '__main__':
    start = time.time()
    f1 = '/Users/antx/Code/tmp/airt/pics/playing/3541824696133615616/LOCAL/TAIL/1.png'
    poker_dia(f1, 1, 1, 1, 1, 1)
    # result = asyncio.run(poker_dia(f1, 1, 1, 1, 1, 1))
    # print(result)
    end = time.time()
    print(f'耗时：{end - start}s.')
