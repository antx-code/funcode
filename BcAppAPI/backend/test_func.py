from utils.services.redis_db_connect.connect import *
from utils.services.base.base_func import *
from io import BytesIO
import re

# from PIL import Image

def test_redis_incr():
	redis_service = redis_connection()
	res = redis_service.redis_client.incr(name='wkaifeng', amount=1)
	print(res)
	print(type(res))
	resp = redis_service.set_dep_key('wkaifeng', res, 90)
	print(resp)

def test_get_user_id():
	mongodb = db_connection('bc-app', 'users')
	result = mongodb.find_one({'email': 'wkaifeng2007@163.com'})
	# for user in result:
	# 	user_id = user['user_id']
	# print(user_id)
	print(result['user_id'])
	print(result)

def test_create_token():
	access_token = create_authtoken(user_id='111', identity='bcb-app')['access_token']
	print(access_token)
	return access_token

def test_mongodb_update_one():
	mongodb = db_connection('bc-app', 'users')
	now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	login_info = {
		'last_login_time': now_time,
		'access_token': test_create_token()
	}
	result = mongodb.update_one({'email': 'wkaifeng2007@163.com'}, login_info)
	print(result)

def number2hex():
	import binascii

	def baseN(num, b):
		return ((num == 0) and "0") or \
		       (baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % b])

	# s = 3470044405556051968
	s = baseN(3470044405556051968, 32)

	print(hex(3470044405556051968))
	print(baseN(3470044405556051968, 32))
	str_16 = binascii.b2a_hex(str(s).encode('utf-8'))  # 字符串转16进制
	print(str_16)

def p64(n: int) -> str:
	table = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
	s = bin(n)[2:][::-1]
	return "".join([table[int(s[i : i + 6][::-1], 2)] for i in range(0, len(s), 6)][::-1])[:8]

def test_snow_flake():
	from utils.services.base.SnowFlake import IdWorker
	id_worker = IdWorker(0, 0)
	user_id = id_worker.get_id()
	print(user_id)
	return user_id

def test_qrcode(promo_code):
	from app.handler.user_handler import generate_qrcode
	generate_qrcode(promo_code)

def save_img():
	with open('promo_code.png', 'rb') as f:
		img = BytesIO(f.read())
	# bimg = bson.binary.Binary(img.getvalue())
	# result = base64.b64encode(bimg).decode('ascii')
	mongodb = db_connection('test', 'test')
	r = mongodb.save_img(3470044405556051968, img)
	print(r)
	# print(result)
	# return result

def restore_img(data=None):
	# ori_data = base64.b64decode(data)
	# with open('test.png', 'wb') as f:
	# 	f.write(ori_data)
	mon = db_connection('test', 'test')
	r = mon.read_img(3470044405556051968, 'test2.png', save_local=True)
	print(r)

def test_phone():
	regre = '\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\W*\d\W*\d\W*\d\W*\d\W*\d\W*\d\W*\d\W*\d\W*(\d{1,2})$'
	phone_number = re.findall(regre, '+8615738368019')
	logger.info(phone_number)

def generate_init_miners():
	from utils.services.redis_db_connect.connect import db_connection
	mongodb = db_connection('bc-app', 'miners')
	miner_info = {
		'miner_name': 'MinerMonkey',
		'miner_month_reward': 1000,
		'miner_power': '4THS',
		'miner_price': 2000,
		'miner_team_price': 1800,
		'miner_manage_price': 0.1,
		'miner_numbers': 10000
	}
	mongodb.insert_one_data(miner_info)

def set_default_avatar():
	from utils.services.redis_db_connect.connect import db_connection
	mongodb = db_connection('bc-app', 'avatar')
	with open('default.png', 'rb') as f:
		png_content = f.read()
	mongodb.save_img(user_id='default', img=png_content)

def init_asset():
	from utils.services.redis_db_connect.connect import db_connection
	asset_db = db_connection('bc-app', 'assets')

	asset_info = {
		'user_id': 3470934271785435136,
		'asset': {
			'usdt': {
				'all': 10000,
				'today_reward': 10,
			},
			'miner': [{
				'miner_id': 0,
				'miner_name': 'MinerSnow',
				'created_time': '2021-06-12 12:12:32',
				'alive_time': '00:00:00',
				'all': 0,
				'today_reward': 0,
			}],
			'team_miner': [{
				'miner_id': 0,
				'miner_name': 'MinerSnow',
				'created_time': '2021-06-12 12:12:32',
				'alive_time': '00:00:00',
				'members': [],  # nickname
				'all': 0,
				'today_rewards': 0,
				'today_reward': 0
			}]
		}
	}
	asset_db.update_one({'user_id': 3470934271785435136}, asset_info)

def genarate_miner_pics():
	from utils.services.redis_db_connect.connect import db_connection
	mongodb = db_connection('bc-app', 'miner_pics')
	with open('miner.png', 'rb') as f:
		png_content = f.read()
	mongodb.save_img(user_id='MinerMonkey', img=png_content)

def init_redis_config():
	import json
	from utils.services.redis_db_connect.connect import redis_connection
	config = {
		'MinerReward':10,
		'Level1Reward':0.2,
		'Level2Reward':0.3,
		'Level3Reward':0.5,
		'MinerManageFee':2,
		'MinerLife':100,
		'ShareReward': 1000,
		'TeamBuyNumber': 7
	}
	redis = redis_connection()
	redis.hset_redis(redis_key='config', content_key='app', content_value=json.dumps(config, ensure_ascii=False))

def test_init_announcement():
	from utils.services.base.SnowFlake import IdWorker
	from utils.services.redis_db_connect.connect import db_connection
	announcement_db = db_connection('bc-app', 'announcement')
	id_worker = IdWorker(0, 0)
	ids = []
	for i in range(5):
		ids.append(id_worker.get_id())
	for inx, id in enumerate(ids):
		now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		announcement = {
			'aid': id,
			'author': 'antx',
			'created_time': now_time,
			'title': f'test for bc app {inx + 1} announcement',
			'content': 'sdfjklhvkjhasnflkjaslkfehfhsladkjfinasljdfjaksm.mcas',
		}
		announcement_db.insert_one_data(announcement)

def test_dnks():
	from backend.app.handler.user_handler import dnetworks
	dnetworks(3470934271785435136, '30Hf5ikw', 'ASDF8778')

def test_promo_code():
	from backend.app.handler.user_handler import generate_qrcode
	generate_qrcode(3472912957086629888, '30Og-YD0')

def time2seconds(st):
	h, m, s = st.strip().split(":")
	time2sec = int(h) * 3600 + int(m) * 60 + int(s)
	print(time2sec)
	return time2sec

def seconds2time(st):
	m, s = divmod(st, 60)
	h, m = divmod(m, 60)
	return h, m, s

def get_recent7date(n=7):
	dates = []
	today = datetime.datetime.now()
	# print(today)
	for i in range(n):
		dates.append((today - datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
	# print(dates)
	return dates

def generate_miner_rewaqd():
	from utils.services.redis_db_connect.connect import db_connection
	miner_reward_db = db_connection('bc-app', 'miner_reward')
	miner_reward = {
		'user_id': 3470934271785435136,
		'miner_type': 'personal',
		'miner_id': 'NO.3472794787',
		'miner_name': 'MinerSnow',
		'miner_created_time': '2021-06-13 02:06:38',
		'miner_except_month_reward': 1000,
		'miner_manage_price': 0.1,
		'miner_power': '4THS',
		'miner_sum_reward': 800,
		'miner_today_reward': 200,
		'miner_running_time': '580:48:00',
		'miner_status': 'running'
	}
	team_miner_reward = {
		'user_id': 3470934271785435136,
		'miner_type': 'team',
		'miner_members': ['leo', 'antxww'],
		'miner_member_count': 2,
		'miner_id': 'NO.3472809053',
		'miner_name': 'MinerMonkey',
		'miner_created_time': '2021-06-13 03:03:20',
		'miner_except_month_reward': 1000,
		'miner_manage_price': 0.1,
		'miner_power': '4THS',
		'miner_sum_reward': 800,
		'miner_today_reward': 200,
		'miner_running_time': '580:48:00',
		'miner_status': 'running'
	}
	miner_reward_db.insert_one_data(miner_reward)
	miner_reward_db.insert_one_data(team_miner_reward)

def generate_miner_reward_record():
	from utils.services.redis_db_connect.connect import db_connection
	reward_record_db = db_connection('bc-app', 'miner_reward_record')
	record = {
		'user_id': 3470934271785435136,
		'miner_type': 'personal',
		'miner_id': 'NO.3472794787',
		'miner_name': 'MinerSnow',
		'miner_reward_record': '2021-06-11',
		'miner_reward': 200,
	}
	team_record = {
		'user_id': 3470934271785435136,
		'miner_type': 'team',
		'miner_members': ['leo', 'antxww'],
		'miner_member_count': 2,
		'miner_id': 'NO.3472809053',
		'miner_name': 'MinerMonkey',
		'miner_reward_record': '2021-06-11',
		'miner_reward': 200,
		'miner_per_reward': 100,
	}
	reward_record_db.insert_one_data(record)
	reward_record_db.insert_one_data(team_record)

def test_query_reward_record():
	from utils.services.redis_db_connect.connect import db_connection
	miner_reward_record_db = db_connection('bc-app', 'miner_reward_record')
	final_records = []
	print(f'gte -> {get_recent7date()[-1]}')
	print(f'lte -> {get_recent7date()[0]}')
	records = miner_reward_record_db.query_data({
		'$and': [{
			'miner_reward_record': {'$gte': get_recent7date()[-1], '$lte': get_recent7date()[0]},
			'user_id': 3470934271785435136,
			'miner_type': 'personal'
		}]
	})
	for record in records:
		del record['_id']
		del record['user_id']
		final_records.append(record)
	print(final_records)

def customer_services():
	from utils.services.redis_db_connect.connect import db_connection
	cs_db = db_connection('bc-app', 'customer_urls')
	url1 = 'http://127.0.0.1:888'
	url2 = 'http://127.0.0.1:999'
	cs_db.insert_one_data({'url': url1})
	cs_db.insert_one_data({'url': url2})

def test_redis_ttl():
	from utils.services.redis_db_connect.connect import redis_connection
	redis = redis_connection()
	expir = redis.redis_client.ttl('aaa')
	print(expir)
	print(type(expir))
	# result = redis.get_key_expire_content('l11')
	# print(result)

def test_math_sa():
	counts = 23
	size = 10
	pages = counts // size
	print(pages)

def timestamp2format():
	timestamp = 1623524130
	tl = time.localtime(timestamp)
	format_time = time.strftime("%Y-%m-%d %H:%M:%S", tl)
	print(format_time)

def test_today():
	today = str(datetime.datetime.today()).split(' ')[0]
	logger.info(today)

if __name__ == '__main__':
	test_math_sa()
	timestamp2format()
	test_today()
	# generate_init_miners()
	# st = time2seconds('12:21:11')
	# h, m, s = seconds2time(2090880)
	# print(f'{h:02d}:{m:02d}:{s:02d}')
	# get_recent7date()
	# generate_miner_rewaqd()
	# generate_miner_reward_record()

	# customer_services()

	# test_query_reward_record()

	# genarate_miner_pics()
	# init_redis_config()
	# test_redis_ttl()

	# set_default_avatar()
	# init_asset()
	# test_init_announcement()
	# test_dnks()
	# test_promo_code()

	# test_phone()
	# test_redis_incr()
	# test_get_user_id()
	# test_create_token()
	# test_mongodb_update_one()
	# number2hex()
	# res = p64(test_snow_flake())
	# res = p64(3470044405556051968)
	# print(res)
	# test_qrcode(res)
	# save_img()
	# restore_img()
