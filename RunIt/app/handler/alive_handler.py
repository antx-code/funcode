from utils.services.db_redis_connect.connect import *
from init import config

CONF = config['DEVICE']

@logger.catch(level='ERROR')
async def aliveH():
    redis_service = redis_connection(redis_db=0)
    if not CONF:
        return 'error', "config error"
    # account_status = redis_service.get_key_expire_content('account')
    # if not account_status:
    #     return 'error', "account error"
    # app_status = redis_service.get_key_expire_content('app')
    # if not app_status:
    #     return 'error', "app error"
    return 'success', "alive"
