from loguru import logger
import time
import asyncio
import httpx
from airtest.core.api import *
from airtest.aircv import *
from comser.funcs import *
import os
from poc import poker_dia
# from comser.background import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

CONF = config['CORP_IMG']
CORP_PLAYER = ['LOCAL', 'PLAYER1', 'PLAYER2']
CORP_POKER = ['HEAD', 'MID', 'TAIL', 'DROP']

POKER_RELA = {
    'LOCAL': 'local',
    'PLAYER1': 'player1',
    'PLAYER2': 'player2',
    'HEAD': 'head',
    'MID': 'mid',
    'TAIL': 'tail',
    'DROP': 'drop',
    # 'HAND': 'hand'
}

now_path = os.getcwd()

# async def ca(task_id, screen, record, SIG):
#     tasks = []
#     for player in CORP_PLAYER:
#         CONF_BASE = CONF[player][SIG] if player != 'LOCAL' else CONF[player]
#         for dao_poker in CORP_POKER:
#             if not CONF_BASE[dao_poker]:
#                 continue
#             for inx, dk in enumerate(CONF_BASE[dao_poker]):  # 对每个位置进行图像分割， 并保存进相应的文件夹
#                 filename = f'{now_path}/pics/playing/{task_id}/{player}/{dao_poker}/{inx}.png'
#                 try:
#                     ci = aircv.crop_image(screen, dk)
#                     aircv.imwrite(filename, ci, quality=99)
#                 except Exception as e:
#                     return
#
#                 tasks.append(poker_dia(filename, task_id, record, POKER_RELA[player], POKER_RELA[dao_poker], inx))
#     await asyncio.gather(*tasks)

async def cac(task_id, screen, record, SIG):
    start1 = time.time()
    tasks = []
    for player in CORP_PLAYER:
        CONF_BASE = CONF[player][SIG] if player != 'LOCAL' else CONF[player]
        for dao_poker in CORP_POKER:
            if not CONF_BASE[dao_poker]:
                continue
            for inx, dk in enumerate(CONF_BASE[dao_poker]):  # 对每个位置进行图像分割， 并保存进相应的文件夹
                filename = f'{now_path}/pics/playing/{task_id}/{player}/{dao_poker}/{inx}.png'
                try:
                    ci = aircv.crop_image(screen, dk)
                    aircv.imwrite(filename, ci, quality=99)
                except Exception as e:
                    return
                # print('bk-pre')
                # bk.add_task(poker_dia, filename, task_id, record, POKER_RELA[player], POKER_RELA[dao_poker], inx)
                await run_in_threadpool(lambda: poker_dia(filename, task_id, record, POKER_RELA[player], POKER_RELA[dao_poker], inx))
                # print('bk-af')

                # tasks.append(poker_dia(filename, task_id, record, POKER_RELA[player], POKER_RELA[dao_poker], inx))
    # await asyncio.gather(*tasks)
    end1 = time.time()
    print(f'poker_dia: {end1 - start1}s')

if __name__ == '__main__':
    start = time.time()
    f1 = '/Users/antx/Code/tmp/airt/pics/playing/3536088477621813248/LOCAL/TAIL/0.png'
    asyncio.run(cac(643734, 'asd'))
    # print(result)
    end = time.time()
    print(f'耗时：{end - start}s.')
