from loguru import logger
import asyncio
import uvloop
from utils.services.redis.redis_service import RedisService
from utils.services.db.async_mongodb import AsyncMongo
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@logger.catch(level='ERROR')
async def db_connection(db, collection, port=27017):
    mongodb = AsyncMongo(db, collection, port)
    return mongodb

@logger.catch(level='ERROR')
def redis_connection(port=6379, redis_db=0):
    redis_service = RedisService(port=port, redis_db=redis_db)
    return redis_service