from redis import Redis
from loguru import logger
import json
import base64
import struct
import numpy
from init import config

class RedisService():
    @logger.catch(level='ERROR')
    def __init__(self, port, redis_db=0, mode='server'):
        if mode == 'server':
            conf = config['REDIS']['SERVER']
            self.redis_client = Redis(host=conf['HOST'], port=port, password=conf['PASSWORD'], db=redis_db)
        else:
            conf = config['REDIS']['LOCAL']
            self.redis_client = Redis(host=conf['HOST'], port=port, db=redis_db)

    @logger.catch(level='ERROR')
    def new_insert_content(self, redis_key, new_content):
        """

        :param redis_key:
        :param new_content: Must be same as the exists data.
        :return:
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

    @logger.catch(level='ERROR')
    def del_redis_element(self, tar_redis_key, tar_element):
        self.redis_client.srem(tar_redis_key, tar_element)
        return True

    @logger.catch(level='ERROR')
    def get_diff_set(self, tar_redis_key, small_redis_key, big_redis_key):
        self.redis_client.sdiffstore(tar_redis_key, big_redis_key, small_redis_key)
        return True

    @logger.catch('ERROR')
    def sscan_redis(self, redis_key, cursor=0, match=None, count=1):
        """

        Use SSCAN method to get redis data, which can set query data's count.

        :param redis_key: The target key that you want to query.
        :param match: The parameter that you want to match.
        :param count: The amount of data that you want to return.
        :return:
        """
        result_list = []
        result = self.redis_client.sscan(name=redis_key, cursor=cursor, match=match, count=count)[1]
        for each_result in result:
            result_list.append(each_result.decode())
        return result_list

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
        try:
            result = self.redis_client.get(key_name)
            return result.decode()
        except Exception as e:
            return None

    @logger.catch('ERROR')
    def hset_redis(self, redis_key, content_key, content_value):
        """

        Insert hash data into redis, which have key and value like python's dic.

        :param redis_key: The redis key that you want to set.
        :param content_key: The key of the hash data.
        :param content_value: The value of the hash data.
        :return: The result of the operate.
        """
        result = self.redis_client.hset(name=redis_key, key=content_key, value=content_value)
        if result:
            return True
        return False

    @logger.catch('ERROR')
    def hget_redis(self, redis_key, content_key):
        """

        The get method of the hash data in redis.

        :param redis_key: The redis key that you want to get.
        :param content_key: The key of the hash data.
        :return: A origin data type of the hash data value.
        """
        resp = self.redis_client.hget(name=redis_key, key=content_key).decode()
        result = json.loads(resp)
        return result



    def numpy_save(self, key: str, numpy_ndarray: numpy.ndarray) -> None:
        """???Numpy????????????Redis????????????

        Parameters
        ----------
        key : str
            ???????????????
        numpy_ndarray : numpy.ndarray
            ??????????????????
        """
        shape = numpy_ndarray.shape
        dim = len(shape)
        value = struct.pack(''.join(['>I'] + ['I' * dim]), *((dim,) + shape))
        value = base64.a85encode(value + numpy_ndarray.tobytes())  # ?????????????????????????????????????????????????????????
        self.redis_client.set(key, value)
        self.redis_client.close()

    def numpy_read(self, key: str, dtype) -> numpy.ndarray:
        """???Redis???????????????Numpy?????????

        Parameters
        ----------
        key : str
            ???????????????
        dtype : Any
            ?????????????????????????????????

        Returns
        -------
        numpy.ndarray
            ???Redis???????????????????????????
        """
        SIZE = 4
        bytes = base64.a85decode(self.redis_client.get(key))
        self.redis_client.close()
        dim = struct.unpack('>I', bytes[:1 * SIZE])[0]
        shape = struct.unpack('>%s' % ('I' * dim), bytes[1 * SIZE:(dim + 1) * SIZE])
        ret = numpy.frombuffer(
            bytes,
            offset=(dim + 1) * SIZE,
            dtype=dtype
        ).reshape(shape)
        return ret
