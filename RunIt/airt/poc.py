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
    num = ddddocr_poker(filename)
    print(f'{filename} poker_dia num: {num}')
    color = poker_max_color(filename)         # 颜色识别
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

    print(f'records[{record_player}][{record_dao_poker}][{inx}]: {records[record_player][record_dao_poker][inx]}')
    if not record and records[record_player][record_dao_poker][inx]:
        pass
    else:
        records[record_player][record_dao_poker][inx] = record
        set_living_status_redis(task_id, {'records': records})

if __name__ == '__main__':
    start = time.time()
    f1 = '/Users/antx/Code/tmp/airt/pics/playing/3536088477621813248/LOCAL/TAIL/0.png'
    result = asyncio.run(poker_dia(f1))
    print(result)
    end = time.time()
    print(f'耗时：{end - start}s.')
