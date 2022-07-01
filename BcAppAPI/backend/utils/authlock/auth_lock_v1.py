from redis import Redis
from loguru import logger

logger.add(sink='logs/auth_lock.log',
           level='ERROR',
           # colorize=True,     # 设置颜色
           format='{time:YYYY-MM-DD  :mm:ss} - {level} - {file} - {line} - {message}',
           enqueue=True,
           # serialize=True,    # 序列化为json
           backtrace=False,
           diagnose=False,   
           rotation='00:00',
           retention='7 days')

class RedisService():
    @logger.catch(level='ERROR')
    def __init__(self, passwd, redis_db):
        self.redis_client = Redis(db=redis_db)

    @logger.catch(level='ERROR')
    def set_dep_key(self, key_name, key_value, expire_secs=None):
        """

        Set a duplicate redis key, which include content and expire time.

        :param key_name: The duplicate redis key that you want to be saved.
        :param key_value: The duplicate content of the redis key
        :param expire_secs: The expire time of the redis key and value. It's default value is None
        :return: A bool value of the operate.
        """
        self.redis_client.set(key_name, key_value, ex=expire_secs)
        return True

    @logger.catch(level='ERROR')
    def get_key_expire_content(self, key_name):
        """

        Get the expire redis key's content.

        :param key_name: The redis key that you want to query.
        :return: A string of the expire content.
        """
        result = self.redis_client.get(key_name)
        if result:
            return result.decode()
        else:
            return False

    @logger.catch(level='ERROR')
    def del_key(self, key_name):
        """

        Delete the expire key.

        :param key_name: The target key name that you want to delete.
        :return: 1 for success or 0 for failed.
        """
        return self.redis_client.delete(key_name)

    @logger.catch(level='ERROR')
    def check_key(self, key_name):
        """

        Check the key is exist in redis or not.

        :param key_name: The key that you want to check.
        :return: If the key is exist in redis, it will return True, otherwise will return False.
        """
        if self.redis_client.exists(key_name):
            return True
        return False

class AuthLock():
    def __init__(self):
        self.redis_service = RedisService(passwd='antx-auth-lock', redis_db=1)
        self.salt = '9_0^9_1'
        self.skey = 'antx-au_^_th-@#_$_?!'

    def generate_auth_code(self, nickname: str, expire_time: int):
        auth_code = 'steam_buff_auth_lock'
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        check_result = self.redis_service.check_key(key_name=nickname)
        if check_result:
            return False
        return self.redis_service.set_dep_key(key_name=nickname, key_value=auth_code, expire_secs=(expire_time * 86400))

    def verify_auth_code(self, nickname: str):
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        result = self.redis_service.get_key_expire_content(key_name=nickname)
        if result:
            return True
        return False

    def del_auth(self, nickname: str):
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        result = self.redis_service.del_key(nickname)
        if result:
            return True
        return False

if __name__ == '__main__':
    auth_lock = AuthLock()

    # 生成授权码
    nickname = input('请输入授权帐号名，请包含数字字母：')
    expire_time = input('请输入授权有效时间，单位/天：')
    auth_code = auth_lock.generate_auth_code(nickname=nickname, expire_time=int(expire_time))
    print(auth_code)

    # # 验证授权码
    # result = auth_lock.verify_auth_code('antx')
    # print(result)
    #
    # # 删除授权码
    # result = auth_lock.del_auth('antx')
    # print(result)
