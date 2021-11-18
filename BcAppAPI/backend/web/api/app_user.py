from fastapi import APIRouter, Depends
from utils.services.base.base_func import *
from utils.services.base.SnowFlake import IdWorker
from web.models.appuser_models import *
from app.handler.user_handler import *

# logger.add(sink='logs/app_user.log',
#            level='ERROR',
#            # colorize=True,     # 设置颜色
#            format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
#            enqueue=True,
#            # serialize=True,    # 序列化为json
#            backtrace=True,   # 设置为'False'可以保证生产中不泄露信息
#            diagnose=True,    # 设置为'False'可以保证生产中不泄露信息
#            rotation='00:00',
#            retention='7 days')

router = APIRouter(dependencies=[Depends(antx_auth)])

user_db = db_connection('bc-app', 'users')
user_info_db = db_connection('bc-app', 'user-info')
promo_db = db_connection('bc-app', 'promo_qrcode')
dnk_db = db_connection('bc-app', 'dnetworks')
miner_db = db_connection('bc-app', 'miners')
asset_db = db_connection('bc-app', 'assets')
miner_pic_db = db_connection('bc-app', 'miner_pics')
record_db = db_connection('bc-app', 'records')
share_buy_db = db_connection('bc-app', 'share_buy_code')
address_db = db_connection('bc-app', 'address')
redis_service = redis_connection(redis_db=0)

id_worker = IdWorker(0, 0)

@logger.catch(level='ERROR')
@router.post('/all')
async def get_all_users(get_info: GetAllUsers):
	users = []
	pref = (get_info.page - 1) * get_info.size
	af = get_info.size
	all_users = user_db.collection.find({}, {"_id": 0}).skip(pref).limit(af)
	for user in all_users:
		promo_invite_info = user_info_db.find_one({'user_id': user['user_id']})
		if not promo_invite_info:
			invite_code = ''
			promo_code = ''
		else:
			invite_code = promo_invite_info['base_info']['share'].get('invite_code', '')
			promo_code = promo_invite_info['base_info']['share'].get('promo_code', '')
		user_info = {
			'user_id': str(user['user_id']),
			'nickname': user['nickname'],
			'phone': user['phone'],
			'email': user['email'],
			'invite_code': invite_code,
			'promo_code': promo_code,
			'register_time': user['created_time'],
			'last_login_time': user['last_login_time'],
			'last_login_ip': user['last_login_ip'],
			'is_logged_in': user['is_logged_in'],
			'is_verified': user['is_verified'],
			'level_status': '',
			'member_status': ''
		}
		users.append(user_info)
	total_count = user_db.collection.find({}, {"_id": 0}).count()
	page_tmp = total_count % af
	if page_tmp != 0:
		all_pages = (total_count // af) + 1
	else:
		all_pages = total_count // af
	rep_data = {'filter_count': len(users), 'record': users, 'total_count': total_count, 'total_pages': all_pages}
	return msg(status='susscss', data=rep_data)

@logger.catch(level='ERROR')
@router.post('/add_user')
async def add_user(add_info: AddUser):
	user_id = id_worker.get_id()  # 生成唯一用户id
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	if add_info.nickname in user_db.dep_data('nickname'):
		return msg(status='error', data='User already exists!')
	pcode = promo_code(user_id)
	user_info = {
		'user_id': user_id,
		'nickname': add_info.nickname,
		'email': add_info.email,
		'phone': add_info.phone,
		'password': result_hash(add_info.init_password),
		'created_time': now_time,
		'last_login_time': '',
		'last_login_ip': '',
		'access_token': '',
		'promo_code': pcode,
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
	profile_info = {
		'user_id': user_id,
		'base_info': {
			'profile': {
				'nickname': add_info.nickname,
				'sex': 'male',
				'area': 'china',
				'intro': '这个家伙很懒，什么都没留下'
			},
			'share': {
				'invite_code': 'INTIAL',
				'promo_code': pcode,
			}
		}
	}
	dnk_info = {
	    "user_id" : user_id,
	    "own_code" : pcode,
	    "pre1_code" : "INTIAL",
	    "pre2_code" : "INTIAL",
	    "pre3_code" : "INTIAL",
	    "af1_code" : [],
	    "af2_code" : []
	}
	user_db.insert_one_data(user_info)
	user_info_db.insert_one_data(profile_info)
	asset_db.insert_one_data(asset_info)
	dnk_db.insert_one_data(dnk_info)
	return msg(status='success', data='Add new app user successfully!')

@logger.catch(level='ERROR')
@router.get('/{user_id}')
async def get_user(user_id):
	user_id = int(user_id)
	if int(user_id) not in user_db.dep_data('user_id') and str(user_id) not in user_db.dep_data('user_id'):
		return msg(status='error', data='User was not exist!')
	user_info = user_db.find_one({'user_id': user_id})
	promo_invite_info = user_info_db.find_one({'user_id': user_id})
	if not promo_invite_info:
		invite_code = ''
		promo_code = ''
	else:
		invite_code = promo_invite_info['base_info']['share']['invite_code']
		promo_code = promo_invite_info['base_info']['share']['promo_code']
	return_info = {
		'user_id': user_id,
		'nickname': user_info['nickname'],
		'phone': user_info['phone'],
		'email': user_info['email'],
		'invite_code': invite_code,
		'promo_code': promo_code,
		'register_time': user_info['created_time'],
		'last_login_time': user_info['last_login_time'],
		'last_login_ip': user_info['last_login_ip'],
		'is_logged_in': user_info['is_logged_in'],
		'is_verified': user_info['is_verified'],
		'level_status': '',
		'member_status': ''
	}
	return msg(status='success', data=return_info)

@logger.catch(level='ERROR')
@router.post('/update_user')
async def update_user(update_info: UpdateUser):
	updates = {}
	if update_info.update_info:
		for inx, (k, v) in enumerate(dict(update_info.update_info).items()):
			if v:
				updates[k] = v
	user_db.update_one({'user_id': int(update_info.user_id)}, updates)
	return msg(status='success', data='Updated user info successfully')

@logger.catch(level='ERROR')
@router.post('/delete_user')
async def delete_user(delete_info: DeleteUser):
	if delete_info.user_id not in user_db.dep_data('user_id'):
		return msg(status='error', data='User not exist!')
	user_db.delete_one({'user_id': int(delete_info.user_id)})
	return msg(status='success', data='User deleted successfully')
