import jwt
from jwt.exceptions import ExpiredSignatureError
from config import CONFIG
from loguru import logger

# @logger.catch(level='ERROR')
# def create_authtoken(identity):
#     payload = {
#         "iat": int(time.time()),
#         "exp": int(time.time()) + 86400 * 7,    # 有效时间7天
#         "scopes": ['open'],
#         "identity": identity
#     }
#     token = jwt.encode(payload, CONFIG['SALT'], algorithm='HS256').decode('utf-8')
#     return {'access_token': token, 'identity': identity}

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
        payload = jwt.decode(token, CONFIG['SALT'], algorithms=['HS256'])
    except ExpiredSignatureError:
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

    # payload = jwt.decode(token, config.SALT, algorithms=['HS256'])
    # return payload