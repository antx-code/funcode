from loguru import logger
import time
from utils.services.redis_db_connect.connect import redis_connection
from utils.services.base.SnowFlake import IdWorker

id_worker = IdWorker(0, 0)

@logger.catch(level='ERROR')
def generate_miner_id():
	miner_id = str(id_worker.get_id())
	return f'NO.{miner_id[2:]}'

@logger.catch(level='ERROR')
def record_recharge_withdraw(user_id, type, count): #
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	exchange_info = {
		'user_id': user_id,
		'record_id': id_worker.get_id(),
		'type': type,
		'created_time': now_time,
		'update_time': '',
		'status': 'pending',
		'count': count
	}
	return exchange_info

@logger.catch(level='ERROR')
def record_reward(user_id, reward, miner_id):
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	reward_info = {
		'user_id': user_id,
		'created_time': now_time,
		'miner_id': miner_id,
		'miner_reward': reward
	}
	return reward_info

@logger.catch(level='ERROR')
def record_buy(user_id, buy_miner_name, buy_miner_id, pay_money, buy_type):
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	buy_info = {
		'user_id': user_id,
		'record_id': id_worker.get_id(),
		'miner_id': buy_miner_id,
		'miner_name': buy_miner_name,
		'pay_money': pay_money,
		'type': buy_type,
		'created_time': now_time
	}
	return buy_info

@logger.catch(level='ERROR')
def generate_share_code_url():
	share_code = str(id_worker.get_id())
	share_url = f'http://74.211.103.41:8889/api/app/exchange/share/{share_code}'
	return share_code, share_url

@logger.catch(level='ERROR')
def share_code_monitor(share_code):
	redis = redis_connection(redis_db=1)
	redis_config = redis_connection()
	CONFIG = redis_config.hget_redis('config', 'app')
	try:
		share_info = redis.get_key_expire_content(key_name=share_code)
		share_code_expire = redis.redis_client.ttl(name=share_code)
		if share_code_expire == -2:
			pass
		else:
			pass
		if share_info['member_count'] == CONFIG['TeamBuyNumber']:
			return True
	except Exception as e:
		pass