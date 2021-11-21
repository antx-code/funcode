import time
from fastapi import Request
import utils.xauth.verify as verify
from utils.exceptions.customs import InvalidPermissions, UnauthorizedAPIRequest, RecordNotFound
from __init__ import config

CONF = config['AUTH']

def auth_required(request):
    """
    权限验证（用户必须有相关权限才能通过验证）
    :param function_to_protect:
    :return:
    """
    # 获取token 内容
    status, auth_token = verify.verify_request(request)
    if not status:
        raise UnauthorizedAPIRequest("Verify token failed, rejecting request!")
    exp_time = auth_token['exp']
    identify = auth_token['identity']
    if identify not in CONF['IDENTITY']:
        raise InvalidPermissions('Unauthorized user, rejecting request!')
    if int(exp_time) < int(time.time()):
        raise UnauthorizedAPIRequest('Token was expired, Please re-login!')
    return True

def verification(request: Request):
    return auth_required(request=request)
