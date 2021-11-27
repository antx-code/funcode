import json
import time
from utils.services.db_redis_connect.connect import *
from utils.services.base.snow_flake import IdWorker

id_worker = IdWorker(0, 0)

@logger.catch(level='ERROR')
def GeTaskId():
    task_id = str(id_worker.get_id())
    return task_id

@logger.catch(level='ERROR')
def now():
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return now_time

@logger.catch(level='ERROR')
async def save_info(db: str, col: str, info: dict):
    session = await db_connection(db, col)
    await session.collection.insert_one(info)

@logger.catch(level='ERROR')
async def update_one(db: str, col: str, task_id: str, new_info: dict):
    session = await db_connection(db, col)
    update_info = {'$set': new_info}
    await session.collection.update_one({'task_id': task_id}, update_info, upsert=True)

@logger.catch(level='ERROR')
async def delete_one(db: str, col: str, task_id: str, mode: str = 'logical'):
    if mode == 'logical':
        await update_one(db, col, task_id, {'is_deleted': True})
    else:
        session = await db_connection(db, col)
        await session.collection.delete_one({'task_id': task_id})

@logger.catch(level='ERROR')
async def query_one_task(mode: str, task_id: str):
    if mode == 'record':
        session = await db_connection('RunIt', 'records')
    else:
        session = await db_connection('RunIt', 'tasks')
    data = await session.collection.find_one({'task_id': task_id}, {'_id':0})
    return data

@logger.catch(level='ERROR')
def set_game_status(status: bool):
    redis_service = redis_connection(redis_db=0)
    redis_service.set_dep_key('playing', json.dumps(status, ensure_ascii=False))

@logger.catch(level='ERROR')
def task_living(task_id: str, info: dict, mode: str = 'new'):
    redis_service = redis_connection(redis_db=1)
    if mode == 'new':
        data = json.dumps(info, ensure_ascii=False)
    else:
        infos = redis_service.get_key_expire_content(task_id)
        data = json.loads(infos)
        data[info['key']] = info['value']
        data = json.dumps(data, ensure_ascii=False)
    redis_service.redis_client.delete('recording')
    redis_service.new_insert_content('recording', task_id)
    redis_service.set_dep_key(task_id, data)

@logger.catch(level='ERROR')
def get_task_living(task_id):
    redis_service = redis_connection(redis_db=1)
    infos = redis_service.get_key_expire_content(task_id)
    data = json.loads(infos)
    return data

def set_living_status_redis(task_id: str, info: dict):
    redis_service = redis_connection(redis_db=1)
    o_datas = redis_service.get_key_expire_content(task_id)
    o_data = json.loads(o_datas)
    for inx, (k, v) in enumerate(info.items()):
        o_data[k] = v
    data = json.dumps(o_data, ensure_ascii=False)
    redis_service.set_dep_key(task_id, data)

@logger.catch(level='ERROR')
async def get_task_list(page: int, size: int):
    db = await db_connection('RunIt', 'tasks')
    records = []
    async for data in db.collection.find({'is_deleted': False}, {'_id': 0}).sort('create_time', -1).skip(page).limit(size):
        del data['is_deleted']
        records.append(data)
    total_count = await db.collection.count_documents({'is_deleted': False})
    return records, total_count

@logger.catch(level='ERROR')
async def create_one_task(task_id: str, task_name: str, room_id: int, mode: str):
    tasks = {
        'task_id': task_id,
        'task_name': task_name,
        'task_mode': mode,
        'room_id': room_id,
        'status': 'pending',
        'is_deleted': False,
        'create_time': now(),
        'update_time': now(),
        'record_time': now()
    }
    await save_info('RunIt', 'tasks', tasks)    # records 由app侧生成
    tasks['records'] = {}
    await save_info('RunIt', 'records', tasks)
    set_game_status(True)
    living_info = {
        'task_name': task_name,
        'task_mode': mode,
        'room_id': room_id,
        'status': 'pending',
        'records': {},  # records 由app侧生成
        'update_time': now()
    }
    task_living(task_id, living_info)
    resp = {
        'task_name': task_name,
        'task_mode': mode,
        'task_id': task_id
    }
    return resp

# @logger.catch(level='ERROR')
# async def get_task_status(task_id: str):
#     data = await query_one_task(mode='record', task_id=task_id)
#     record = {
#         'task_name': data['task_name'],
#         'task_mode': data['task_mode'],
#         'room_id': data['room_id'],
#         'status': data['status'],
#         'update_time': data['update_time'],
#         'records': data['records']
#     }
#     return record

@logger.catch(level='ERROR')
async def get_task_status(task_id: str):
    data = get_task_living(task_id)
    return data

@logger.catch(level='ERROR')
async def stop_one_task(task_id: str):
    status = 'stopped'
    update_info = {'status': status}
    await update_one('RunIt', 'tasks', task_id, update_info)
    await update_one('RunIt', 'records', task_id, update_info)
    set_game_status(False)
    redis_status = {
        'key': 'status',
        'value': status
    }
    task_living(task_id, redis_status, mode='update')
    record = {
        'task_id': task_id,
        'is_stopped': True
    }
    return record

@logger.catch(level='ERROR')
async def delete_one_task(task_id: str):
    await delete_one('RunIt', 'tasks', task_id)
    await delete_one('RunIt', 'records', task_id)
    record = {
        'task_id': task_id,
        'is_deleted': True
    }
    return record

@logger.catch(level='ERROR')
async def get_one_record(task_id: str):
    record = await query_one_task(mode='record', task_id=task_id)
    del record['is_deleted']
    # record = get_task_living(task_id)
    return record

@logger.catch(level='ERROR')
async def save_one_play_record(task_id: str, room: int, status: str, record: dict):
    # dict_record = json.loads(record)
    update_info = {'records': record}
    set_living_status_redis(task_id, {'records': record})
    set_living_status_redis(task_id, {'status': status})
    set_living_status_redis(task_id, {'update_time': now()})
    await update_one('RunIt', 'tasks', task_id, update_info)
    await update_one('RunIt', 'tasks', task_id, {'status': status})
    await update_one('RunIt', 'records', task_id, update_info)
    await update_one('RunIt', 'records', task_id, {'status': status})
    return {'task_id': task_id, 'room': room}
