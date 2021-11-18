from fastapi import APIRouter, Depends
from utils.services.base.base_func import *
from utils.services.redis_db_connect.connect import *
from app.models.user_info_models import *

# logger.add(sink='logs/user_info_api.log',
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
avatar_db = db_connection('bc-app', 'avatar')
asset_db = db_connection('bc-app', 'assets')
redis_service = redis_connection(redis_db=0)

# @logger.catch(level='ERROR')
# @router.get('/members')
# async def get_team_members(request: Request, dep=Depends(antx_auth)):
# 	user_id = dep
# 	logger.info(user_id)
# 	members = []
# 	af_info = dnk_db.find_one({'user_id': user_id})
# 	af1_codes = af_info.get('af1_code', [])
# 	af2_codes = af_info.get('af2_code', [])
# 	all_reward = 0
# 	for af1_code in af1_codes:
# 		logger.info(f'query af1_code->{af1_code}')
# 		af1_user_info = user_db.find_one({'promo_code': af1_code})
# 		af1_user_id = af1_user_info['user_id']
# 		af1_nickname = af1_user_info['nickname']
# 		try:
# 			af1_avatar = avatar_db.find_one({'user_id': af1_user_id})['avatar']
# 		except Exception as e:
# 			af1_avatar = avatar_db.find_one({'user_id': 'default'})['img']
# 		reward = asset_db.find_one({'user_id': user_id})['asset']['share']
# 		all_reward += reward
# 		members.append({'nickname': af1_nickname, 'avatar': af1_avatar, 'reward': reward})
#
# 	for af2_code in af2_codes:
# 		af2_user_info = user_db.find_one({'promo_code': af2_code})
# 		af2_user_id = af2_user_info['user_id']
# 		af2_nickname = af2_user_info['nickname']
# 		try:
# 			af2_avatar = avatar_db.find_one({'user_id': af2_user_id})['avatar']
# 		except Exception as e:
# 			af2_avatar = avatar_db.find_one({'user_id': 'default'})['img']
# 		reward = asset_db.find_one({'user_id': user_id})['asset']['share']
# 		all_reward += reward
# 		members.append({'nickname': af2_nickname, 'avatar': af2_avatar, 'reward': reward})
# 	final_result = {
# 		'all_reward': all_reward,
# 		'members': members
# 	}
# 	return msg(status='success', data=final_result)

def level_deal(af_codes):
	logger.info(af_codes)
	results = []
	try:
		for code in af_codes:
			af_dnk_info = dnk_db.find_one({'own_code': code})
			af_id = af_dnk_info['user_id']
			af_info = user_db.find_one({'user_id': af_id})
			af1_code = af_dnk_info['af1_code']
			af2_code = af_dnk_info['af2_code']
			af12_codes = af1_code + af2_code
			nickname = af_info['nickname']
			register_time = af_info['created_time']
			last_login_time = af_info['last_login_time']
			recommend_number = len(af12_codes)
			team_reward = 0
			af_asset_info = asset_db.find_one({'user_id': af_id})
			personal_reward = af_asset_info['asset'].get('share', 0)
			logger.info(f'af12_codes->{af12_codes}')
			for af12_code in af12_codes:
				af12_id = dnk_db.find_one({'own_code': af12_code})['user_id']
				try:
					each_asset = asset_db.find_one({'user_id': af12_id})['asset']
				except Exception as e:
					each_asset = {'share': 0}
				team_reward += each_asset.get('share', 0)
			af_final_info = {
				'nickname': nickname,
				'recommend_munber': recommend_number,
				'team_reward': team_reward,
				'personal_reward': personal_reward,
				'register_time': register_time,
				'last_login_time': last_login_time
			}
			results.append(af_final_info)
	except Exception as e:
		results = []
	return results

@logger.catch(level='ERROR')
@router.get('/member/{level}')
async def get_my_team(request: Request, level):
	user_id = antx_auth(request)
	dnk_info = dnk_db.find_one({'user_id': user_id})
	asset_info = asset_db.find_one({'user_id': user_id})
	all_reward = 0  # 总收益
	team_reward = 0  # 每个团员的share总和 == 团队总收益
	af1_codes = dnk_info['af1_code']
	af2_codes = dnk_info['af2_code']
	af_codes = af1_codes + af2_codes
	for af_code in af_codes:
		af_id = dnk_db.find_one({'own_code': af_code})['user_id']
		af_asset_info = asset_db.find_one({'user_id': af_id})['asset']
		team_reward += af_asset_info.get('share', 0)
	personal_reward = asset_info['asset'].get('share', 0)  # -> 等于own_reward等于all_reward
	own_reward = personal_reward
	all_reward = personal_reward
	team_sum_reward = team_reward
	if int(level) == 1: # 自己层
		user_info = user_db.find_one({'user_id': user_id})
		nickname = user_info['nickname']
		register_time = user_info['created_time']
		last_login_time = user_info['last_login_time']
		recommend_munber = len(af1_codes) + len(af2_codes)
		team_reward = 0 # 每个团员的share总和 == 团队总收益
		final_result = {
			'team_sum_reward': team_sum_reward,
			'all_reward': all_reward,
			'own_reward': own_reward,
			'level1_result': [{
				'username': nickname,
				'recommend_munber': recommend_munber,
				'team_reward': team_reward,
				'personal_reward': personal_reward,
				'register_time': register_time,
				'last_login_time': last_login_time
			}]
		}
		return msg(status='success', data=final_result)
	elif int(level) == 2:   # 下级, 作为自己的一级，向下探索两级
		level2_results = level_deal(af1_codes)
		final_result = {
			'team_sum_reward': team_sum_reward,
			'all_reward': all_reward,
			'own_reward': own_reward,
			'level2_result': level2_results
		}
		return msg(status='success', data=final_result)
	elif int(level) == 3:   # 下级的下级
		level3_results = level_deal(af2_codes)
		final_result = {
			'team_sum_reward': team_sum_reward,
			'all_reward': all_reward,
			'own_reward': own_reward,
			'level3_result': level3_results
		}
		return msg(status='success', data=final_result)
	else:
		return msg(status='error', data='Out of level range!', code=213)

