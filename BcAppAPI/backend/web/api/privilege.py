from fastapi import APIRouter, Depends
from utils.services.base.base_func import *
from utils.services.redis_db_connect.connect import *
from utils.services.base.SnowFlake import IdWorker
from web.models.privilege_models import *

id_worker = IdWorker(0, 0)

# logger.add(sink='logs/privilege.log',   (包含公告和活动)
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
admin_db = db_connection('bc-web', 'admin_users')
redis_service = redis_connection(redis_db=0)

@logger.catch(level='ERROR')
@router.post('/list')
async def get_privilege_list(privilege_info: PrivilegeList):
	privileges = []
	pref = (privilege_info.page - 1) * privilege_info.size
	af = privilege_info.size
	if privilege_info.type == 'user':
		users_info = user_db.collection.find({}, {'_id': 0}).skip(pref).limit(af)
		for user in users_info:
			user_info = {
				'user_id': str(user['user_id']),
				'username': user['nickname'],
				'privilege': user.get('privilege', 'user'),
				'is_active': user['is_active'],
				'is_superuser': user['is_superuser'],
				'is_logged_in': user['is_logged_in']
			}
			privileges.append(user_info)
		total_count = user_db.collection.find({}, {"_id": 0}).count()
	else:
		users_info = admin_db.collection.find({'privilege': privilege_info.type}, {'_id': 0}).skip(pref).limit(af)
		for user in users_info:
			user_info = {
				'user_id': str(user['user_id']),
				'username': user['username'],
				'privilege': user.get('privilege', 'gensuper'),
				'is_active': user['is_active'],
				'is_superuser': user['is_superuser'],
				'is_logged_in': user['is_logged_in']
			}
			privileges.append(user_info)
		total_count = admin_db.collection.find({'privilege': privilege_info.type}, {"_id": 0}).count()
		page_tmp = total_count % af
		if page_tmp != 0:
			all_pages = (total_count // af) + 1
		else:
			all_pages = total_count // af
		rep_data = {'filter_count': len(privileges), 'record': privileges, 'total_count': total_count, 'total_pages': all_pages}
	return msg(status='success', data=rep_data)

@logger.catch(level='ERROR')
@router.get('/{user_id}')
async def get_user_privilege(user_id):
	user_id = int(user_id)
	tag = 'user'
	user_info = user_db.find_one({'user_id': user_id})
	if not user_info:
		tag = 'non-user'
		user_info = admin_db.find_one({'user_id': user_id})
	info = {
		'user_id': str(user_info['user_id']),
		'privilege': user_info.get('privilege', 'user'),
		'is_active': user_info['is_active'],
		'is_superuser': user_info['is_superuser'],
		'is_logged_in': user_info['is_logged_in']
	}
	if tag == 'non-user':
		info['username'] = user_info['username']
	else:
		info['username'] = user_info['nickname']
	return msg(status='success', data=info)

@logger.catch(level='ERROR')
@router.post('/set_privilege')
async def set_privilege(set_info: SetPrivilege):
	updates = {}
	pri = dict(set_info)
	del pri['user_id']
	for inx, (k, v) in enumerate(pri.items()):
		if v:
			updates[k] = v
	if set_info.privilege == 'user':
		user_db.update_one({'user_id': int(set_info.user_id)}, updates)
	else:
		admin_db.update_one({'user_id': int(set_info.user_id)}, updates)
	return msg(status='success', data='Set user privilege successfully')