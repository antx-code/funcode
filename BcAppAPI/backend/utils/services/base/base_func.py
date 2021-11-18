from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
import time, datetime
import json
import jwt
from bson import ObjectId
from fastapi import Request
import hashlib
from utils.services.auth.antx_auth import auth_required
from config import CONFIG

logger.add(sink='logs/base_func.log',
           level='ERROR',
           # colorize=True,     # 设置颜色
           format='{time:YYYY-MM-DD  :mm:ss} - {level} - {file} - {line} - {message}',
           enqueue=True,
           # serialize=True,    # 序列化为json
           backtrace=True,   # 设置为'False'可以保证生产中不泄露信息
           diagnose=True,    # 设置为'False'可以保证生产中不泄露信息
           rotation='00:00',
           retention='7 days')

@logger.catch(level='ERROR')
def msg(status, data, code=None):
    if code:
        final_data = {'status': status, 'code': code, 'message':data}
    else:
        final_data = {'message':data, 'status':status}
    return JSONResponse(content=jsonable_encoder(final_data))

@logger.catch(level='ERROR')
def object_id_from_datetime(from_datetime=None):
    ''' According to the time manually generated an ObjectId '''
    if not from_datetime:
        from_datetime = datetime.datetime.now()
    return ObjectId.from_datetime(generation_time=from_datetime)

@logger.catch(level='ERROR')
def create_authtoken(user_id, identity):
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7,    # 有效时间7天
        "user_id": user_id,
        "identity": identity
    }
    token = jwt.encode(payload, CONFIG['SALT'], algorithm='HS256')
    return {'access_token': token}

def antx_auth(request: Request):
    return auth_required(request=request)

@logger.catch(level='ERROR')
def time2timestamp(tar_time: str, time_format: str):
    time_array = time.strptime(tar_time, time_format)
    timestamp = time.mktime(time_array)
    return int(timestamp)

@logger.catch(level='ERROR')
def md5_hash(_str):
    hl = hashlib.md5()
    hl.update(_str.encode(encoding="utf-8"))
    return hl.hexdigest()

@logger.catch(level='ERROR')
def result_hash(result):
    return md5_hash(json.dumps(result, ensure_ascii=False))

@logger.catch(level='ERROR')
def get_diff_list(small_list, big_list):
    """
    Get the difference set of the two list.
    :param small_list: The small data list.
    :param big_list: The bigger data list.
    :return: diff_list: The difference set list of the two list.
    """
    # big_list有而small_list没有的元素
    diff_list = list(set(big_list).difference(set(small_list)))
    return diff_list
