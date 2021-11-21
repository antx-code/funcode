from loguru import logger
import time
import jwt
from __init__ import config

CONF = config['AUTH']

@logger.catch(level='ERROR')
def create_authtoken(identity):
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7,    # 有效时间7天
        "scopes": ['open'],
        "identity": identity
    }
    token = jwt.encode(payload, CONF['SALT'], algorithm='HS256')
    return {'access_token': token, 'identity': identity}
