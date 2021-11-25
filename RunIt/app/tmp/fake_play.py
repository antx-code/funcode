import json
import time
import asyncio
import uvloop
import sys
# sys.path.append('/home/antx/Code/tmp/funcode/RunIt/app/')
sys.path.append('/home/yonglin/RunIt/app')
from random import randint as rant
from utils.services.db_redis_connect.connect import *
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def set_status(task_id, status):
    db = await db_connection('RunIt', 'tasks')
    update_info = {'$set': {'status': status}}
    db.collection.update_one({'task_id': task_id}, update_info, upsert=True)

async def set_record_status(task_id, status):
    db = await db_connection('RunIt', 'records')
    update_info = {'$set': {'status': status}}
    db.collection.update_one({'task_id': task_id}, update_info, upsert=True)

async def get_status(task_id):
    db = await db_connection('RunIt', 'tasks')
    info = await db.collection.find_one({'task_id': task_id})
    return info['status']

async def update_record(task_id, record):
    db = await db_connection('RunIt', 'records')
    update_info = {'$set': {'records': record}}
    db.collection.update_one({'task_id': task_id}, update_info, upsert=True)


fake_datas = [
    {
        'local': {
            'head': [None, None, None],
            'mid': [None, None, None, None, None],
            'tail': [14, 46, 48, 36, 34],
            'drop': [None, None, None, None]
        },
        'player1': {
            'head': [None, None, None],
            'mid': [None, None, None, None, None],
            'tail': [14, 46, 48, 36, 34],
            'drop': [None, None, None, None]
        },
        'player2': {
            'head': [None, None, None],
            'mid': [None, None, None, None, None],
            'tail': [29, 38, 8, 49, 4],
            'drop': [None, None, None, None]
        }
    },
    {
            'local': {
                'head': [47, 41, None],
                'mid': [None, None, None, None, None],
                'tail': [14, 46, 48, 36, 34],
                'drop': [5, None, None, None]
            },
            'player1': {
                'head': [47, 41, None],
                'mid': [None, None, None, None, None],
                'tail': [14, 46, 48, 36, 34],
                'drop': [5, None, None, None]
            },
            'player2': {
                'head': [20, 3, None],
                'mid': [None, None, None, None, None],
                'tail': [29, 38, 8, 49, 4],
                'drop': [24, None, None, None]
            }
        },
    {
            'local': {
                'head': [50, 47, 41],
                'mid': [11, None, None, None, None],
                'tail': [14, 46, 48, 36, 34],
                'drop': [5, 0, None, None]
            },
            'player1': {
                'head': [50, 47, 41],
                'mid': [11, None, None, None, None],
                'tail': [14, 46, 48, 36, 34],
                'drop': [5, 0, None, None]
            },
            'player2': {
                'head': [20, 6, 3],
                'mid': [45, None, None, None, None],
                'tail': [29, 38, 8, 49, 4],
                'drop': [24, 18, None, None]
            }
        },
    {
            'local': {
                'head': [50, 47, 41],
                'mid': [11, 10, 19, None, None],
                'tail': [14, 46, 48, 36, 34],
                'drop': [5, 0, 13, None]
            },
            'player1': {
                'head': [50, 47, 41],
                'mid': [11, 10, 19, None, None],
                'tail': [14, 46, 48, 36, 34],
                'drop': [5, 0, 13, None]
            },
            'player2': {
                'head': [20, 6, 3],
                'mid': [45, 12, 2, None, None],
                'tail': [29, 38, 8, 49, 4],
                'drop': [24, 18, 35, None]
            }
        },
    {
        'local': {
            'head': [50, 47, 41],
            'mid': [11, 10, 19, 27, 39],
            'tail': [14, 46, 48, 36, 34],
            'drop': [5, 0, 13, 33]
        },
        'player1': {
            'head': [50, 47, 41],
            'mid': [11, 10, 19, 27, 39],
            'tail': [14, 46, 48, 36, 34],
            'drop': [5, 0, 13, 33]
        },
        'player2': {
            'head': [20, 6, 3],
            'mid': [45, 44, 25, 12, 2],
            'tail': [29, 38, 8, 49, 4],
            'drop': [24, 18, 35, 21]
        }
    }
]

class FakePlay():
    def __init__(self):
        self.redis_service = redis_connection(redis_db=1)

    async def generate_fake_data(self, task_id: str, fake_data: dict):
        fake_db = await db_connection('RunIt', 'FakeData')
        info = {
            'task_id': task_id,
            'fake_data': fake_data
        }
        fake_db.collection.insert_one(info)

    async def fake(self, task_id: str):
        fake_db = await db_connection('RunIt', 'FakeData')
        async for data in fake_db.collection.find({'task_id': task_id}).sort('_id', 1):
            print(data)
            record = data['fake_data']
            await update_record(task_id, record)
            await asyncio.sleep(rant(2, 4))

    async def fake_connecting(self, task_id: str):
        i = rant(3, 6)
        while i >= 0:
            await asyncio.sleep(1)
            i = i - 1
            await set_status(task_id, 'connecting')
        await set_status(task_id, 'capturing')
        await set_record_status(task_id, 'capturing')

    async def fake_plays(self):
        task_ids = self.redis_service.read_redis('fakePlay')
        for task_id in task_ids:
            i = 30
            for fake_data in fake_datas:
                await self.generate_fake_data(task_id, fake_data)
            await self.fake_connecting(task_id)
            while i >= 0:
                status = await get_status(task_id)
                if status == 'stopped' or status == 'finished':
                    break
                await self.fake(task_id)
                i = i - 1
            await set_status(task_id, 'finished')
            await set_record_status(task_id, 'finished')
        # self.redis_service.redis_client.delete('fakePlay')
        return False

if __name__ == '__main__':
    fp = FakePlay()
    while True:
        sig = asyncio.run(fp.fake_plays())
        if not sig:
            continue
