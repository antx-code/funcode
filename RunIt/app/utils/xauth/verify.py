import jwt
from loguru import logger
from __init__ import config

CONF = config['AUTH']

@logger.catch(level='ERROR')
def get_authorization(request):
    authorization = request.headers.get('Authorization')
    if not authorization:
        return False, None
    try:
        authorization_type, token = authorization.split(' ')
        return authorization_type, token
    except ValueError:
        return False, None

@logger.catch(level='ERROR')
def verify_authtoken(token):
    try:
        payload = jwt.decode(token, CONF['SALT'], algorithms=['HS256'])
    except Exception as e:
        return False, token
    if payload:
        return True, dict([(str(key), value) for key, value in payload.items()])        # 将payload转换为字典
    return False, token

@logger.catch(level='ERROR')
def verify_request(request):
    authorization_type, token = get_authorization(request)
    if authorization_type == 'Bearer':
        return verify_authtoken(token)
    return False, None
