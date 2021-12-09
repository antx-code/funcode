import json
import time
import asyncio
import uvloop
import httpx
import sys
from loguru import logger
import jwt
from init import config
# sys.path.append('/home/antx/Code/tmp/funcode/RunIt/app/')
sys.path.append('/home/yonglin/RunIt/app')
from comser.redis_service import RedisService
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

@logger.catch(level='ERROR')
def now():
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return now_time

def create_token():
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7,  # 有效时间7天
        "scopes": ['open'],
        "identity": 'dev'
    }
    token = jwt.encode(payload, '913059', algorithm='HS256')
    # return {'access_token': token, 'identity': 'dev'}
    return token

@logger.catch(level='ERROR')
def redis_connection(redis_db=0, mode='server'):
    if mode == 'server':
        db_port = config['REDIS']['SERVER']['PORT']
    else:
        db_port = config['REDIS']['LOCAL']['PORT']
    redis_service = RedisService(port=db_port, redis_db=redis_db, mode=mode)
    return redis_service

@logger.catch(level='ERROR')
def set_living_status_redis(task_id: str, info: dict):
    redis_service = redis_connection(redis_db=1)
    o_datas = redis_service.get_key_expire_content(task_id)
    o_data = json.loads(o_datas)
    for inx, (k, v) in enumerate(info.items()):
        o_data[k] = v
    data = json.dumps(o_data, ensure_ascii=False)
    redis_service.set_dep_key(task_id, data)

@logger.catch(level='ERROR')
def get_living_status(task_id):
    redis_service = redis_connection(redis_db=1)
    infos = redis_service.get_key_expire_content(task_id)
    data = json.loads(infos)
    return data['status']

def get_playing_room_taskid():
    redis_service = redis_connection(redis_db=1)
    try:
        task_id = redis_service.read_redis('recording')[0]
    except Exception as e:
        return None, None
    infos = redis_service.get_key_expire_content(task_id)
    data = json.loads(infos)
    return task_id, data['room_id']

@logger.catch(level='ERROR')
async def push_record2serv(task_id: str, room: int, status: str, record: dict):
    url = 'http://120.131.14.155:8019/api/app/storage_record'
    header = {'Authorization': f'Bearer {create_token()}'}
    post_data = {
        "task_id": task_id,
        "room": room,
        "status": status,
        "record": record
    }
    async with httpx.AsyncClient(verify=False, timeout=5, headers=header) as client:
        resp = await client.post(url, json=post_data)
        logger.info(resp)
    return True

@logger.catch(level='ERROR')
def del_redis_record(task_id):
    redis_service = redis_connection(redis_db=1)
    redis_service.redis_client.srem('recording', task_id)
