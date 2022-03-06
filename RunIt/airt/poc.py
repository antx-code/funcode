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

    max_color, color_dict, color_list, no_max_color = poker_max_color(filename)         # 颜色识别

    print(f'max_color: {max_color}, color_dict: {color_dict}, color_list: {color_list}, no_max_color: {no_max_color}')

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
    print(f'********** poker number: {record} **********')

    logger.warning(f'records[{record_player}][{record_dao_poker}][{inx}]: {records[record_player][record_dao_poker][inx]}')

    if records[record_player][record_dao_poker][inx] == -1 and record != -1:
        records[record_player][record_dao_poker][inx] = record

if __name__ == '__main__':
    start = time.time()
    f1 = '/pics/playing/3541824696133615616/LOCAL/TAIL/1.png'
    poker_dia(f1, 1, 1, 1, 1, 1)
    end = time.time()
    print(f'耗时：{end - start}s.')
