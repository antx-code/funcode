from fastapi import APIRouter, Depends
from utils.exceptions.customs import InvalidPermissions
from utils.services.base.base_func import *
from utils.services.base.SnowFlake import IdWorker
from utils.services.redis_db_connect.connect import *
from web.models.admin_models import *

# logger.add(sink='logs/admin.log',
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

admin_db = db_connection('bc-web', 'admin_users')
redis_service = redis_connection(redis_db=0)

@logger.catch(level='ERROR')
@router.post('/all', summary='获取所有管理员账户信息')
async def get_all_admin(request: Request, get_info: AllAdmin):
	final_data = []
	pref = (get_info.page - 1) * get_info.size
	af = get_info.size
	all_admins = admin_db.collection.find({}, {'_id': 0}).skip(pref).limit(af)
	for admin in all_admins:
		admin['user_id'] = str(admin['user_id'])
		admin['created_by'] = str(admin['created_by'])
		final_data.append(admin)
	total_count = admin_db.collection.find({}, {'_id': 0}).count()
	page_tmp = total_count % af
	if page_tmp != 0:
		all_pages = (total_count // af) + 1
	else:
		all_pages = total_count // af
	rep_data = {'filter_count': len(final_data), 'record': final_data, 'total_count': total_count, 'total_pages': all_pages}
	return msg(status='success', data=rep_data)

@logger.catch(level='ERROR')
@router.post('/login', summary='管理员登陆')
async def login(request: Request, login_info: AdminLogin):
	admin_username_infos = admin_db.dep_data('username')
	if login_info.username not in admin_username_infos:
		return msg(status='error', data='User was not exist!')
	admin_info = admin_db.find_one({'username': login_info.username})
	admin_user_id = admin_info['user_id']
	if login_info.username in redis_service.read_redis(redis_key='locked_admin_account'):
		return msg(status="error", data="Admin account was locked!")

	if result_hash(login_info.password) != admin_info['password']:
		failed_login_count = redis_service.redis_client.incr(name=admin_user_id, amount=1)
		redis_service.set_dep_key(key_name=admin_user_id, key_value=failed_login_count, expire_secs=90)
		if failed_login_count == 5:
			redis_service.new_insert_content(redis_key='locked_admin_account', new_content=login_info.username)
			admin_db.update_one({'user_id': admin_user_id}, {'is_active': False})
			return msg(status="error", data="The number of login times has exceeded the limit, and the account has been locked")
		return msg(status='error', data=f"Username or password was not correct，only {5 - failed_login_count} times to retry!")
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	access_token = create_authtoken(user_id=admin_user_id, identity='bc-web')['access_token']
	record_info = {'last_login_time': now_time, 'last_login_ip': request.client.host, 'is_logged_in': True, 'access_token': access_token}
	admin_db.update_one({'username': login_info.username}, record_info)
	return msg(status='success', data={'access_token': access_token})

@logger.catch(level='ERROR')
@router.get('/logout')
async def loggout(request: Request, dep=Depends(antx_auth)):
	user_id = antx_auth(request)
	is_logged_in = admin_db.find_one({'user_id': user_id})['is_logged_in']
	if not is_logged_in:
		raise InvalidPermissions("Account have been logged out，token is unavailable!")
	admin_db.update_one({'user_id': user_id}, {'is_logged_in': False})
	return msg(status='success', data='Logout')

@logger.catch(level='ERROR')
@router.post('/reset_password')
async def reset_password(request: Request, reset_info: ResetPassword, dep=Depends(antx_auth)):
	user_id = antx_auth(request)
	old_password = admin_db.find_one({'user_id': user_id})['password']
	if result_hash(reset_info.old_password) != old_password:
		return msg(status="error", data="Old password was incorrect, please try again!")
	if result_hash(reset_info.new_password) != result_hash(reset_info.new_repassword):
		return msg(status="error", data="Two passwordsare not the same, please check!")

	update_info = {"password": result_hash(reset_info.new_password), 'is_logged_in': False}
	admin_db.update_one({'user_id': user_id}, update_info)
	return msg(status='success', data='Reset your password successfully, please login again.')

@logger.catch(level='ERROR')
@router.post('/forgot_password')
async def forgot_password(forgot_info: ForgotPassword):
	if forgot_info.auth_code != 'antx':
		return msg(status='error', data='Not allowed to operate!')
	username_infos = admin_db.dep_data('username')
	if forgot_info.username not in username_infos:
		return msg(status='error', data='Not a available username!')
	if result_hash(forgot_info.new_password) != result_hash(forgot_info.new_repassword):
		return msg(status='error', data='Two passwords were not equal!')
	update_info = {'password': result_hash(forgot_info.new_password)}
	admin_db.update_one({'username': forgot_info.username}, update_info)
	return msg(status='success', data='Reset password successfully')

@logger.catch(level='ERROR')
@router.post('/add_user')
async def add_admin_user(request: Request, add_info: AddNewAdminAcount, dep=Depends(antx_auth)):
	admin_user_id = antx_auth(request)
	admin_user_info = admin_db.find_one({'user_id': admin_user_id})
	privilege = admin_user_info['is_superuser']
	if not privilege:
		return msg(status='error', data='Account was not superuser, hava not privilege!')
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	id_worker = IdWorker(0, 0)
	user_id = id_worker.get_id()  # 生成唯一用户id
	new_info = {
		'username': add_info.username,
		'password': result_hash(add_info.init_password),
		'privilege': add_info.privilege,
		'created_time': now_time,
		'user_id': user_id,
		'created_by': admin_user_id,
		'last_login_time': '',
		'last_login_ip': request.client.host,
		'access_token': '',
		'is_active': True,
		'is_superuser': True,
		'is_logged_in': False
	}
	admin_db.insert_one_data(new_info)
	return msg(status='success', data=f'Add new admin user: {add_info.username}')

@logger.catch(level='ERROR')
@router.post('/delete_user')
async def delete_admin_user(request: Request, delete_info: DeleteAdminAcount, dep=Depends(antx_auth)):
	admin_user_id = antx_auth(request)
	admin_user_info = admin_db.find_one({'user_id': admin_user_id})
	privilege = admin_user_info['is_superuser']
	if not privilege:
		return msg(status='error', data='Account was not superuser, have not privilege!')
	if admin_user_id == admin_db.find_one({'username': delete_info.username})['user_id']:
		return msg(status='error', data='Can not delete yourself!')
	if delete_info.username == 'admin':
		return msg(status='error', data='Can not delete initial admin user!')
	admin_db.delete_one({'username': delete_info.username})
	return msg(status='success', data=f'Delete admin user: {delete_info.username}!')

@logger.catch(level='ERROR')
@router.get('/init_admin')
async def init_admin():
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	id_worker = IdWorker(0, 0)
	user_id = id_worker.get_id()  # 生成唯一用户id
	new_info = {
		'username': 'admin',
		'password': result_hash('admin'),
		'privilege': 'superuser',
		'created_time': now_time,
		'user_id': user_id,
		'created_by': 'system',
		'last_login_time': '',
		'last_login_ip': '',
		'access_token': '',
		'is_active': True,
		'is_superuser': True,
		'is_logged_in': False
	}
	admin_db.insert_one_data(new_info)
	return msg(status='success', data='Add new admin user: admin')

@logger.catch(level='ERROR')
@router.post('/get_bussiness_config')
async def get_bussiness_config(request: Request):
	user_id = antx_auth(request)
	user_info = admin_db.find_one({'user_id': user_id})
	if not user_info['privilege'] or not user_info['is_superuser']:
		return msg(status='error', data='Have not enough privilege to operate!')
	app_config = redis_service.hget_redis(redis_key='config', content_key='app')
	return msg(status='success', data=app_config)

@logger.catch(level='ERROR')
@router.post('/bussiness_config')
async def set_bussiness_config(request: Request, config_info: BussinessConfig, dep=Depends(antx_auth)):
	user_id = antx_auth(request)
	user_info = admin_db.find_one({'user_id': user_id})
	if not user_info['privilege'] or not user_info['is_superuser']:
		return msg(status='error', data='Have not enough privilege to operate!')
	redis_service.hset_redis(redis_key='config', content_key='app', content_value=json.dumps(dict(config_info), ensure_ascii=False))
	return msg(status='success', data='Setting up configuration successfully')

@logger.catch(level='ERROR')
@router.post('/system_settings')
async def set_system_settings(request: Request, config_info: SystemSettings, dep=Depends(antx_auth)):
	user_id = antx_auth(request)
	user_info = admin_db.find_one({'user_id': user_id})
	if not user_info['privilege'] or not user_info['is_superuser']:
		return msg(status='error', data='Have not enough privilege to operate!')
	redis_service.hset_redis(redis_key='config', content_key='web', content_value=json.dumps(dict(config_info), ensure_ascii=False))
	return msg(status='success', data='Setting up system configuration successfully')
