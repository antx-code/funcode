from loguru import logger
from utils.services.redis.redis_service import RedisService
from utils.services.db.mongodb import MongoDB

@logger.catch(level='ERROR')
def db_connection(db, collection):
    mongodb = MongoDB(db, collection)
    return mongodb

@logger.catch(level='ERROR')
def redis_connection(redis_db=0):
    redis_service = RedisService(redis_db=redis_db)
    return redis_service