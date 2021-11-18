import time
from loguru import logger
import utils.services.auth.auth as auth
from utils.services.redis_db_connect.connect import *
from utils.exceptions.customs import InvalidPermissions, UnauthorizedAPIRequest, RecordNotFound
from config import CONFIG

logger.add(sink='logs/antx_auth.log',
           level='ERROR',
           # colorize=True,     # 设置颜色
           format='{time:YYYY-MM-DD  :mm:ss} - {level} - {file} - {line} - {message}',
           enqueue=True,
           # serialize=True,    # 序列化为json
           backtrace=True,   # 设置为'False'可以保证生产中不泄露信息
           diagnose=True,    # 设置为'False'可以保证生产中不泄露信息
           rotation='00:00',
           retention='7 days')


def auth_required(request):
    """
    权限验证（用户必须有相关权限才能通过验证）
    :param function_to_protect:
    :return:
    """
    # 获取token 内容
    status, auth_token = auth.verify_request(request)
    app_db = db_connection('bc-app', 'users')
    web_db = db_connection('bc-web', 'admin_users')
    if status:
        exp_time = auth_token['exp']
        identify = auth_token['identity']
        user_id = auth_token['user_id']
        if identify not in CONFIG['IDENTITY']:
            raise InvalidPermissions('Unauthorized user, rejecting request!')
        if user_id not in app_db.dep_data('user_id') and user_id not in web_db.dep_data('user_id'):
            raise RecordNotFound('User is not exist, rejecting request!')
        if int(exp_time) < int(time.time()):
            raise UnauthorizedAPIRequest('Token was expired, Please re-login!')
        return user_id
    else:
        raise UnauthorizedAPIRequest("Verify token failed, rejecting request!")