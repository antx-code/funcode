from fastapi import APIRouter, Depends
from utils.services.base.base_func import *
from app.handler.miner_handler import *
from utils.services.redis_db_connect.connect import *
from app.handler.exchange_handler import *
from app.models.exchange_models import *

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

# router = APIRouter()

user_db = db_connection('bc-app', 'users')
user_info_db = db_connection('bc-app', 'user-info')
promo_db = db_connection('bc-app', 'promo_qrcode')
dnk_db = db_connection('bc-app', 'dnetworks')
miner_db = db_connection('bc-app', 'miners')
asset_db = db_connection('bc-app', 'assets')
miner_pic_db = db_connection('bc-app', 'miner_pics')
record_db = db_connection('bc-app', 'records')
share_buy_db = db_connection('bc-app', 'share_buy_code')
redis_service = redis_connection(redis_db=0)
notice_db = db_connection('bc-app', 'notices')
address_db = db_connection('bc-app', 'address')

CONFIG = redis_service.hget_redis(redis_key='config', content_key='app')


@logger.catch(level='ERROR')
def get_miner_pic(miner_name=None):
	if not miner_name:
		all_pics = []
		result = miner_pic_db.query_data()
		for pic in result:
			del pic['_id']
			all_pics.append(pic)
		return all_pics
	else:
		result = miner_pic_db.find_one({'user_id': miner_name})
		return result

@logger.catch(level='ERROR')
@router.get('/personal_miners')
async def get_personal_miners():
	miners = []
	result = miner_db.query_data()
	# miner_pics = get_miner_pic()
	for miner in result:
		if miner['miner_price'] == 0:
			continue
		try:
			miner_pic = miner_pic_db.find_one({'user_id': miner['miner_name']})['img']
		except Exception as e:
			miner_pic = miner_pic_db.find_one({'user_id': 'default_miner'})['img']
		del miner['_id']
		del miner['miner_team_price']
		miner['miner_pic'] = miner_pic
		miners.append(miner)
	return msg(status='success', data=miners)

@logger.catch(level='ERROR')
@router.get('/team_miners')
async def get_team_miners():
	miners = []
	result = miner_db.query_data()
	# miner_pics = get_miner_pic()
	for miner in result:
		if miner['miner_team_price'] == 0:
			continue
		try:
			miner_pic = miner_pic_db.find_one({'user_id': miner['miner_name']})['img']
		except Exception as e:
			miner_pic = miner_pic_db.find_one({'user_id': 'default_miner'})['img']
		miner['miner_pic'] = miner_pic
		del miner['_id']
		del miner['miner_price']
		miners.append(miner)
	return msg(status='success', data=miners)

@logger.catch(level='ERROR')
@router.get('/miner/{miner_name}')
async def get_one_miner(miner_name):
	miner_info = miner_db.find_one({'miner_name': miner_name})
	try:
		miner_pic = miner_pic_db.find_one({'user_id': miner_name})['img']
	except Exception as e:
		miner_pic = miner_pic_db.find_one({'user_id': 'default_miner'})['img']
	del miner_info['miner_team_price']
	miner_info['miner_pic'] = miner_pic
	return msg(status='success', data=miner_info)

@logger.catch(level='ERROR')
@router.get('/team_miner/{miner_name}')
async def get_one_miner(miner_name):
	miner_info = miner_db.find_one({'miner_name': miner_name})
	try:
		miner_pic = miner_pic_db.find_one({'user_id': miner_name})['img']
	except Exception as e:
		miner_pic = miner_pic_db.find_one({'user_id': 'default_miner'})['img']
	del miner_info['miner_price']
	miner_info['miner_pic'] = miner_pic
	return msg(status='success', data=miner_info)

@logger.catch(level='ERROR')
@router.post('/buy_miner')
async def buy_miner(request: Request, buy_info: BuyMiner):
	user_id = antx_auth(request)
	asset = asset_db.find_one({'user_id': user_id})['asset']['usdt']['all']
	if asset < buy_info.miner_price:
		return msg(status='error', data='Order created failed, your balance is not enough to buy, please recharge!', code=209)

	miner_info = miner_db.find_one({'miner_name': buy_info.miner_name})
	miner_numbers = miner_info['miner_numbers']

	miner_id = generate_miner_id()

	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	return_info = {
		'miner_id': miner_id,
		'miner_name': buy_info.miner_name,
		'pay_money': buy_info.miner_price,
		'created_time': now_time
	}
	asset_miner = {
		'miner_id': miner_id,
		'miner_name': buy_info.miner_name,
		'created_time': now_time,
		'alive_time': '00:00:00',
		'all': 0,
		'today_reward': 0,
	}
	miner_db.update_one({'miner_name': buy_info.miner_name}, {'miner_numbers': miner_numbers - 1})
	asset_db.update_one({'user_id': user_id}, {'asset.usdt.all': asset - buy_info.miner_price})
	asset_db.collection.update_one({'user_id': user_id}, {'$push': {'asset.miner': asset_miner}}, upsert=True)
	record_db.insert_one_data(record_buy(user_id, buy_info.miner_name, miner_id, buy_info.miner_price, buy_type='personal'))
	return msg(status='success', data=return_info)

@logger.catch(level='ERROR')
@router.post('/post_notice')    # 发送团购邀请
async def post_notice(request: Request, post_info: PostNotice):
	user_id = antx_auth(request)
	nickname = user_db.find_one({'user_id': user_id})['nickname']
	if not post_info.phone:
		noticed_id = user_db.find_one({'email': post_info.email})['user_id']
	else:
		noticed_id = user_db.find_one({'phone': post_info.phone})['user_id']
	share_code, share_url = generate_share_code_url()
	redis_share_info = {
		'team_header': user_id,
		'members': [user_id],  # 包括团长
		'member_count': 1,
		'team_buy_number': CONFIG['TeamBuyNumber'],
		'miner_name': post_info.miner_name
	}
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	db_share_info = {
		'team_header': user_id,
		'created_time': now_time,
		'update_time': '',
		'members': [],
		'member_count': 0,
		'team_buy_number': CONFIG['TeamBuyNumber'],
		'miner_name': post_info.miner_name,
		'status': 'Created'
	}
	notice_info = {
		'team_header': user_id,
		'noticed_id': noticed_id,
		'noticed_detail': f'You friend {nickname} invite you to buy a miner!',
		'share_code': share_code,
		'miner_name': post_info.miner_name,
		'share_url': share_url,
		'created_time': now_time,
	}

	redis = redis_connection(redis_db=1)
	redis.set_dep_key(key_name=share_code, key_value=json.dumps(redis_share_info, ensure_ascii=False), expire_secs=1800)
	share_buy_db.insert_one_data({'share_code': share_code, 'share_info': db_share_info})
	notice_db.insert_one_data(notice_info)
	return msg(status='success', data='Invite request was send, please wait for it.')

@logger.catch(level='ERROR')
@router.get('/get_notice')  # 获取团购邀请信息
async def get_notice(request: Request):
	user_id = antx_auth(request)
	all_notice = []
	try:
		notices = notice_db.collection.find({'noticed_id': user_id}, {'_id': 0}).sort('created_time', -1)
	except Exception as e:
		return msg(status='success', data={'share_code': '', 'miner_name': '', 'notice': ''})
	for notice in notices:
		all_notice.append(notice)
	notice_info = all_notice[0]
	notice = notice_info['noticed_detail']
	share_code = notice_info['share_code']
	miner_name = notice_info['miner_name']
	return msg(status='success', data={'share_code': share_code, 'miner_name': miner_name, 'notice': notice})

@logger.catch(level='ERROR')
@router.post('/share_buy')  # 生成团购邀请码和邀请链接
async def share_buy(request: Request, share_buy: ShareBuy):
	user_id = antx_auth(request)
	share_code, share_url = generate_share_code_url()
	user_asset = asset_db.find_one({'user_id': user_id})['asset']
	miner_id = generate_miner_id()
	miner_price = miner_db.find_one({'miner_name': share_buy.miner_name})['miner_price']
	redis_share_info = {
		'team_header': user_id,
		'members': [user_id],  # 包括团长
		'member_count': 1,
		'team_buy_number': CONFIG['TeamBuyNumber'],
		'miner_name': share_buy.miner_name,
		'miner_id': miner_id
	}
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	db_share_info = {
		'team_header': user_id,
		'created_time': now_time,
		'update_time': '',
		'members': [user_id],
		'member_count': 1,
		'team_buy_number': CONFIG['TeamBuyNumber'],
		'miner_name': share_buy.miner_name,
		'miner_id': miner_id,
		'status': 'Created'
	}

	asset_miner = {
		'miner_id': miner_id,
		'miner_name': share_buy.miner_name,
		'created_time': now_time,
		'update_time': '',
		'alive_time': '00:00:00',
		'members': [user_id],  # user_id 列表
		'member_count': 1,
		'share_code': share_code,
		'all': 0,
		'today_rewards': 0,  # 今日总收益
		'today_reward': 0  # 今日个人收益 = 今日总收益 / 团队人数
	}

	redis = redis_connection(redis_db=1)
	redis.set_dep_key(key_name=share_code, key_value=json.dumps(redis_share_info, ensure_ascii=False), expire_secs=1800)
	share_buy_db.insert_one_data({'share_code': share_code, 'share_info': db_share_info})
	asset_db.update_one({'user_id': user_id}, {'asset.usdt.all': user_asset['usdt']['all'] - miner_price})
	asset_db.collection.update_one({'user_id': user_id}, {'$push': {'asset.team_miner': asset_miner}}, upsert=True)
	record_db.insert_one_data(record_buy(user_id, share_buy.miner_name, miner_id, miner_price, buy_type='team'))
	return msg(status='success', data={'share_code': share_code, 'share_url': share_url})

@logger.catch(level='ERROR')
@router.get('/get_share_code')  # 获取团购邀请码
async def get_share_code(request: Request):
	user_id = antx_auth(request)
	share_codes = []
	results = []
	redis = redis_connection(redis_db=1)
	share_infos = share_buy_db.query_data({'share_info.team_header': user_id})
	for share_info in share_infos:
		share_codes.append(share_info['share_code'])
	logger.info(share_codes)
	for code in share_codes:
		expires = redis.redis_client.ttl(name=code)
		if expires == -2:
			results.append({'share_code': code, 'status': 'Share buy url was expired!'})
		else:
			results.append({'share_code': code, 'status': 'Active'})
	return msg(status='success', data=results)

@logger.catch(level='ERROR')
@router.get('/share/{share_code}')  # 记录加入团购的人
async def share_buy_code(request: Request, share_code):
	user_id = antx_auth(request)
	redis = redis_connection(redis_db=1)
	expires = redis.redis_client.ttl(name=share_code)
	logger.info(expires)
	db_share_info = share_buy_db.find_one({'share_code': share_code})['share_info']
	if expires == -2:
		now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		db_share_info['update_time'] = now_time
		db_share_info['status'] = 'Cannel'
		share_buy_db.update_one({'share_code': share_code}, {'share_info': db_share_info})
		refund = miner_db.find_one({'miner_name': db_share_info['miner_name']})['miner_team_price']
		miner_id = db_share_info['miner_id']
		refund_money(share_code, round((refund/CONFIG['TeamBuyNumber']), 4), miner_id)
		return msg(status='error', data='Share buy url was expired!', code=212)
	redis_share_info = redis.get_key_expire_content(key_name=share_code)
	redis_share_info = json.loads(redis_share_info)
	redis_share_info['members'].append(user_id)
	share_buy_count = redis_share_info['member_count']
	if share_buy_count > CONFIG['TeamBuyNumber']:
		return msg(status='error', data='Number of buyers exceeded!', code=211)
	elif share_buy_count == CONFIG['TeamBuyNumber']:
		return msg(status='success', data='Congratulations, team share buy number is full!')
	redis_share_info['member_count'] += 1
	redis.set_dep_key(key_name=share_code, key_value=json.dumps(redis_share_info, ensure_ascii=False), expire_secs=expires)
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	db_share_info['update_time'] = now_time
	db_share_info['members'].append(user_id)
	db_share_info['member_count'] += 1
	db_share_info['status'] = 'Active'
	share_buy_db.update_one({'share_code': share_code}, {'share_info': db_share_info})
	return msg(status='success', data='Click success, please wating for more team share buy member!')

@logger.catch(level='ERROR')
@router.get('/share_monitor/{share_code}')  # 监测团购码和团购链接的有效性
async def share_monitor(request: Request, share_code):
# def share_monitor(share_code):
	redis = redis_connection(redis_db=1)
	expires = redis.redis_client.ttl(name=share_code)
	db_share_info = share_buy_db.find_one({'share_code': share_code})['share_info']
	if expires == -2:
		now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		db_share_info['update_time'] = now_time
		db_share_info['status'] = 'Cannel'
		share_buy_db.update_one({'share_code': share_code}, {'share_info': db_share_info})
		refund = miner_db.find_one({'miner_name': db_share_info['miner_name']})['miner_team_price']
		try:
			miner_id = db_share_info['miner_id']
		except Exception as e:
			miner_id = generate_miner_id()
			share_buy_db.update_one({'share_code': share_code}, {'miner_id': miner_id})
		# refund_money(share_code, round((refund / CONFIG['TeamBuyNumber']), 4), miner_id)
		return msg(status='error', data='Share buy url was expired!', code=212)
	redis_share_info = redis.get_key_expire_content(key_name=share_code)
	redis_share_info = json.loads(redis_share_info)
	share_buy_count = redis_share_info['member_count']
	if share_buy_count > CONFIG['TeamBuyNumber']:
		return msg(status='error', data='Number of buyers exceeded!', code=211)
	elif share_buy_count == CONFIG['TeamBuyNumber']:
		return msg(status='success', data='Congratulations, team share buy number is full, please pay money!')
	else:
		return msg(status='success', data='Wating for more team share buy member!')

def refund_money(share_buy_code, miner_per_price, miner_id):    # 团购未成功，退回金额并删除资产中团购矿机记录
	share_buy_info = share_buy_db.find_one({'share_code': share_buy_code})['share_info']
	members = share_buy_info['members']
	# member_count = share_buy_info['member_count']
	for member in members:
		logger.info(member)
		user_asset = asset_db.find_one({'user_id': member})['asset']
		user_asset_all = user_asset['usdt']['all']
		logger.info(f'refund {miner_per_price} usdt for {member}...')
		asset_db.update_one({'user_id': member}, {'asset.usdt.all': round(user_asset_all + miner_per_price, 4)})
		asset_db.collection.update({'user_id': member}, {'$pull': {'asset.team_miner': {'miner_id': miner_id}}})

@logger.catch(level='ERROR')
@router.post('/team_share_buy') # 团购购买付款链接
async def team_share_buy_miner(request: Request, buy_info: TeamBuyMiner):
	user_id = antx_auth(request)
	user_asset = asset_db.find_one({'user_id': user_id})['asset']
	redis = redis_connection(redis_db=1)
	share_buy_info = redis.get_key_expire_content(buy_info.share_buy_code)
	share_buy_info = json.loads(share_buy_info)
	members = share_buy_info['members']
	member_count = share_buy_info['member_count']
	miner_id = share_buy_info['miner_id']
	if user_asset['usdt']['all'] < buy_info.miner_per_price:
		return msg(status='error', data='Order created failed, your wallet balance is not enough to buy, please recharge!', code=209)

	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	return_info = {
		'miner_id': miner_id,
		'miner_name': buy_info.miner_name,
		'pay_money': buy_info.miner_per_price,
		'wallet_balance': user_asset['usdt']['all'] - buy_info.miner_per_price,
		'order_created_time': now_time
	}
	asset_miner = {
		'miner_id': miner_id,
		'miner_name': buy_info.miner_name,
		'created_time': now_time,
		'update_time': '',
		'alive_time': '00:00:00',
		'members': members,  # user_id 列表
		'member_count': member_count,
		'share_code': buy_info.share_buy_code,
		'all': 0,
		'today_rewards': 0, # 今日总收益
		'today_reward': 0   # 今日个人收益 = 今日总收益 / 团队人数
	}
	asset_db.update_one({'user_id': user_id}, {'asset.usdt.all': user_asset['usdt']['all'] - buy_info.miner_per_price})
	asset_db.collection.update_one({'user_id': user_id}, {'$push': {'asset.team_miner': asset_miner}}, upsert=True)
	record_db.insert_one_data(record_buy(user_id, buy_info.miner_name, miner_id, buy_info.miner_per_price, buy_type='team'))

	# miner_info = miner_db.find_one({'miner_name': buy_info.miner_name})
	# miner_numbers = miner_info['miner_numbers']
	# miner_db.update_one({'miner_name': buy_info.miner_name}, {'miner_numbers': miner_numbers - 1})
	return msg(status='success', data=return_info)

@logger.catch(level='ERROR')
@router.post('/recharge')
async def recharge(request: Request, recharge_info: RechargeInfo):
	user_id = antx_auth(request)
	asset = asset_db.find_one({'user_id': user_id})['asset']['usdt']['all']
	asset_db.update_one({'user_id': user_id}, {'asset.usdt.all': asset + recharge_info.recharge_usdt})
	record_db.insert_one_data(record_recharge_withdraw(user_id, 'recharge', recharge_info.recharge_usdt))
	return msg(status='success', data="Recharge request success, please waiting for process!")

@logger.catch(level='ERROR')
@router.post('/withdraw')
async def withdraw(request: Request, withdraw_info: WithdrawInfo):
	user_id = antx_auth(request)
	try:
		address = address_db.find_one({'user_id': user_id})['address']
	except Exception as e:
		return msg(status='error', data='Unbinding address!', code=210)
	asset = asset_db.find_one({'user_id': user_id})['asset']['usdt']['all']
	asset_db.update_one({'user_id': user_id}, {'asset.usdt.all': asset - withdraw_info.withdraw_usdt})
	record_db.insert_one_data(record_recharge_withdraw(user_id, 'withdraw', withdraw_info.withdraw_usdt))
	return msg(status='success', data="Withdraw request success, please waiting for process!")

@logger.catch(level='ERROR')
@router.post('/record')
async def get_record(request: Request, record_info: RecordInfo):
	user_id = antx_auth(request)
	final_records = []
	records = record_db.query_data({
		'$and': [{
			'created_time': {'$gte': record_info.record_scope['start'], '$lt': record_info.record_scope['end']},
			'user_id': user_id,
			'type': record_info.record_type
		}]
	})
	for record in records:
		del record['_id']
		final_records.append(record)
	return msg(status='success', data=final_records)

