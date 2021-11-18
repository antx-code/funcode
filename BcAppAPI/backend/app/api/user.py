from fastapi import APIRouter, Depends
from utils.exceptions.customs import InvalidPermissions
from utils.services.base.base_func import *
from utils.services.base.SnowFlake import IdWorker
from app.models.user_models import *
from app.handler.user_handler import *

# logger.add(sink='logs/users_api.log',
#            level='ERROR',
#            # colorize=True,     # 设置颜色
#            format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
#            enqueue=True,
#            # serialize=True,    # 序列化为json
#            backtrace=True,   # 设置为'False'可以保证生产中不泄露信息
#            diagnose=True,    # 设置为'False'可以保证生产中不泄露信息
#            rotation='00:00',
#            retention='7 days')

# router = APIRouter(dependencies=[Depends(antx_auth)])

router = APIRouter()

id_worker = IdWorker(0, 0)
mongodb = db_connection('bc-app', 'users')
asset_db = db_connection('bc-app', 'assets')
redis_service = redis_connection(redis_db=0)

# CONFIG = redis_service.hget_redis('config', 'app')

@logger.catch(level='ERROR')
@router.post('/register')
async def register(user_info: UserRegister, request: Request):
    # 判断两次密码是否一致
    # 判断email是否已经注册
    # 判断昵称是否已经被占用
    if not user_info.password or not user_info.repassword:
        return msg(status='error', data='Password cannot be empty!', code=203)
    if user_info.password != user_info.repassword:
        return msg(status='error', data="Two password are not the same, please check!!", code=204)
    if user_info.nickname in mongodb.dep_data('nickname'):
        return msg(status='error', data="Nickname was already used!", code=205)

    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    user_id = id_worker.get_id()  # 生成唯一用户id
    pcode = promo_code(user_id)
    save_info = {
        'user_id': user_id,
        'nickname': user_info.nickname,
        'email': '',
        'phone': '',
        'password': result_hash(user_info.password),
        'created_time': now_time,
        'last_login_time': '',
        'last_login_ip': request.client.host,
        'access_token': '',
        'promo_code': pcode,
        'privilege': 'user',
        'is_active': True,
        'is_verified': True,
        'is_superuser': False,
        'is_logged_in': False
    }
    asset_info = {
        'user_id': user_id,
        'asset': {
            'usdt': {
                'all': 0,
                'sum_reward': 0,
                'today_reward': 0,
            },
            'miner': [],
            'team_miner': [],
            'share': 0
        }
    }

    if not user_info.phone:
        if '@' not in user_info.email or 'com' not in user_info.email:
            return msg(status='error', data='Please enter right email address!', code=206)
        if user_info.email in mongodb.dep_data('email'):
            return msg(status='error', data="Email was already used!", code=205)
        username = user_info.email
        save_info['email'] = username
    else:
        try:
            ph = int(user_info.phone[1:])
        except Exception as e:
            return msg(status='error', data='Please enter right phone number!', code=206)
        if user_info.phone in mongodb.dep_data('phone'):
            return msg(status='error', data="Phone was already used!", code=205)
        username = user_info.phone
        save_info['phone'] = username

    mongodb.insert_one_data(save_info)
    asset_db.insert_one_data(asset_info)
    generate_qrcode(user_id, pcode)
    dnetworks(user_id=user_id, promo_code=pcode, invite_code=user_info.invite_code)
    return msg(status='success', data=after_register(username, user_info.nickname, user_id))

@logger.catch(level='ERROR')
@router.post('/login')
async def login(user_info: UserLogin, request: Request):
    if user_info.email:
        # if not mongodb.find_one({'email': user_info.email})['is_verified']:
        #     return msg(status="登陆失败", data="账号未进行安全认证")
        #     return RedirectResponse(url='/api/app/user/verify')
        user_id = mongodb.find_one({'email': user_info.email})['user_id']
        update_login_info = {'email': user_info.email}
        if user_info.email in redis_service.read_redis(redis_key='locked_account'):
            return msg(status="error", data="Account was locked，please contact customer service!", code=201)
        if user_info.email not in mongodb.dep_data('email'):
            return msg(status='error', data="User does not exist, please register first!", code=200)
        if result_hash(user_info.password) != mongodb.find_one({'email': user_info.email})['password']:

            failed_login_count = redis_service.redis_client.incr(name=user_id, amount=1)
            redis_service.set_dep_key(key_name=user_id, key_value=failed_login_count, expire_secs=90)
            if failed_login_count == 5:
                redis_service.new_insert_content(redis_key='locked_account', new_content=user_info.email)
                mongodb.update_one({'user_id': user_id}, {'is_active': False})
                return msg(status="error", data="The number of login times has exceeded the limit, and the account has been locked!", code=207)
            return msg(status='error', data=f"Password was incorrect，only {5-failed_login_count} times to retry!", code=207)

    elif user_info.phone:
        try:
            user_id = mongodb.find_one({'phone': user_info.phone})['user_id']
        except Exception as e:
            return msg(status='error', data='Please enter right phone number!', code=206)
        update_login_info = {'phone': user_info.phone}
        if result_hash(user_info.password) != mongodb.find_one({'phone': user_info.phone})['password']:

            failed_login_count = redis_service.redis_client.incr(name=user_id, amount=1)
            redis_service.set_dep_key(key_name=user_id, key_value=failed_login_count, expire_secs=90)
            if failed_login_count == 5:
                redis_service.new_insert_content(redis_key='locked_account', new_content=user_info.phone)
                mongodb.update_one({'user_id': user_id}, {'is_active': False})
                return msg(status="error", data="The number of login times has exceeded the limit, and the account has been locked", code=207)
            return msg(status='error', data=f"Password was incorrect，only {5 - failed_login_count} times to retry!", code=207)

    # user_id = mongodb.find_one({'email': user_info.email})['user_id']
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    access_token = create_authtoken(user_id=user_id, identity='bc-app')['access_token']
    login_info = {'last_login_time': now_time, 'last_login_ip': request.client.host, 'is_logged_in': True, 'access_token': access_token}
    mongodb.update_one(update_login_info, login_info)
    return msg(status='success', data={'access_token': access_token})

@logger.catch(level='ERROR')
@router.post('/logout')
async def logout(user_info: UserLogout, dep=Depends(antx_auth)):
    is_logged_in = mongodb.find_one({'user_id': dep})['is_logged_in']
    if not is_logged_in:
        raise InvalidPermissions("Account have been logged out，token is unavailable!")
    if user_info.email:
        mongodb.update_one({'email': user_info.email}, {'is_logged_in': False})
        return msg(status='success', data='Logout')
    mongodb.update_one({'phone': user_info.phone}, {'is_logged_in': False})
    return msg(status='success', data='Logout')

@logger.catch(level='ERROR')
@router.post('/forgot_password')
async def forgot_password(user_info: UserResetPassword, dep=Depends(antx_auth)):
    is_logged_in = mongodb.find_one({'user_id': dep})['is_logged_in']
    if not is_logged_in:
        raise InvalidPermissions("Account have been logged out，please log in again!")

    if result_hash(user_info.new_password) != result_hash(user_info.new_repassword):
        return msg(status="error", data="Two passwords are not the same，please check!", code=204)

    update_info = {"password": result_hash(user_info.new_password), 'is_logged_in': False}
    mongodb.update_one({'phone': user_info.phone}, update_info)
    user_id = mongodb.find_one({''})
    access_token = create_authtoken(user_id=user_id, identity='bc-app')['access_token']
    return msg(status='success', data={'access_token': access_token})

@logger.catch(level='ERROR')
@router.post('/reset_password')
async def reset_password(user_info: UserResetPassword, dep=Depends(antx_auth)):
    is_logged_in = mongodb.find_one({'user_id': dep})['is_logged_in']
    if not is_logged_in:
        raise InvalidPermissions("Account have been logged out，please log in again!")

    if result_hash(user_info.old_password) != mongodb.find_one({'user_id': dep})['password']:
        return msg(status="error", data="Old password was incorrect, please try again!", code=208)
    if result_hash(user_info.new_password) != result_hash(user_info.new_repassword):
        return msg(status="error", data="Two passwordsare not the same, please check!", code=204)

    update_info = {"password": result_hash(user_info.new_password), 'is_logged_in': False}
    mongodb.update_one({'phone': user_info.phone}, update_info)
    user_id = mongodb.find_one({''})
    access_token = create_authtoken(user_id=user_id, identity='bc-app')['access_token']
    return msg(status='success', data={'access_token': access_token})

@logger.catch(level='ERROR')
@router.post('/get_verify_code')
async def get_verify_code(verify_info: UserVerify):
    if verify_info.verify_type == 'email':
        pass
    else:
        pass
    return msg(status="success", data="verify code has been send, please check!")

@logger.catch(level='ERROR')
@router.post('/verify')
async def verify(verify_info: UserVerify):
    if verify_info.verify_type == 'email':
        pass
    else:
        pass
    return msg(status="success", data="Account has been verified!")
