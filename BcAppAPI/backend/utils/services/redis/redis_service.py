from redis import Redis
from loguru import logger
import json

logger.add(sink='logs/redis_service.log',
           level='ERROR',
           # colorize=True,     # 设置颜色
           format='{time:YYYY-MM-DD  :mm:ss} - {level} - {file} - {line} - {message}',
           enqueue=True,
           # serialize=True,    # 序列化为json
           backtrace=True,  # 设置为'False'可以保证生产中不泄露信息
           diagnose=True,  # 设置为'False'可以保证生产中不泄露信息
           rotation='00:00',
           retention='7 days')


class RedisService():
    @logger.catch(level='ERROR')
    def __init__(self, port=6379, redis_db=0):
        self.redis_client = Redis(port=port, db=redis_db)

    @logger.catch(level='ERROR')
    def new_insert_content(self, redis_key, new_content):
        """
        将数据插入redis，如果数据不存在，返回1,如果数据已经存在，则不插入并返回0
        :param redis_key: The redis key that you want to operate.
        :param new_cobntent: The data that you want to insert and judge. Must be same as the exists data.
        :return: A bool value of the operate.
        """
        if self.redis_client.sadd(redis_key, new_content) == 1:
            return True
        return False

    @logger.catch(level='ERROR')
    def read_redis(self, redis_key):
        data_list = []
        data_set = self.redis_client.smembers(redis_key)
        for each_data in data_set:
            data_list.append(each_data.decode())
        return data_list

    @logger.catch('ERROR')
    def sscan_redis(self, redis_key, match=None, count=1):
        result_list = []
        result = self.redis_client.sscan(name=redis_key,match=match,count=count)[1]
        for each_result in result:
            result_list.append(each_result.decode())
        return result_list

    @logger.catch(level='ERROR')
    def set_dep_key(self, key_name, key_value, expire_secs=None):
        self.redis_client.set(key_name, key_value, ex=expire_secs)
        return True

    @logger.catch(level='ERROR')
    def get_key_expire_content(self, key_name):
        try:
            result = self.redis_client.get(key_name).decode()
        except Exception as e:
            result = self.redis_client.get(key_name)
        return result

    @logger.catch('ERROR')
    def hset_redis(self, redis_key, content_key, content_value):
        result = self.redis_client.hset(name=redis_key, key=content_key, value=content_value)
        if result:
            return True
        return False

    @logger.catch('ERROR')
    def hget_redis(self, redis_key, content_key):
        resp = self.redis_client.hget(name=redis_key, key=content_key).decode()
        result = json.loads(resp)
        return result

    @logger.catch(level='ERROR')
    def get_all_keys(self):
        keys = []
        all_keys = self.redis_client.keys()
        for each_key in all_keys:
            keys.append(each_key.decode())
        return keys