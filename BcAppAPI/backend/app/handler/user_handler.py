from loguru import logger
import qrcode
from io import BytesIO
from utils.services.redis_db_connect.connect import *
import subprocess

@logger.catch(level='ERROR')
def after_register(email_phone, nickname, user_id):
	after_register_info = {
		'nickname': nickname,
		'user_id': user_id
	}
	try:
		ph = int(email_phone.phone[1:])
		after_register_info['phone'] = email_phone
	except Exception as e:
		after_register_info['email'] = email_phone
	return after_register_info

@logger.catch(level='ERROR')
async def verify_code(user_id, verify_type, code):
    pass

@logger.catch(level='ERROR')
def promo_code(user_id: int) -> str:
	table = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
	s = bin(user_id)[2:][::-1]
	return "".join([table[int(s[i : i + 6][::-1], 2)] for i in range(0, len(s), 6)][::-1])[:8]

@logger.catch(level='ERROR')
def generate_qrcode(user_id, promo_code):
	mongodb = db_connection('bc-app', 'promo_qrcode')
	qr = qrcode.QRCode(
		version=5,  # 二维码的大小，取值1-40
		box_size=10,  # 二维码最小正方形的像素数量
		error_correction=qrcode.constants.ERROR_CORRECT_H,  # 二维码的纠错等级
		border=5  # 白色边框的大小
	)
	qr.add_data(promo_code)  # 设置二维码数据
	img = qr.make_image()  # 创建二维码图片
	img.save(f'{promo_code}_qrcode.png')  # 保存二维码make()
	with open(f'{promo_code}_qrcode.png', 'rb') as f:
		img_png = BytesIO(f.read())
	mongodb.save_img(user_id=user_id, img=img_png, img_name=promo_code, qr_code=True)
	subprocess.run(f'rm {promo_code}_qrcode.png', shell=True)

@logger.catch(level='ERROR')
def dnetworks(user_id, promo_code, invite_code):
	dnk_db = db_connection('bc-app', 'dnetworks')
	users = dnk_db.dep_data('user_id')
	asset_db = db_connection('bc-app', 'assets')
	redis_service = redis_connection(redis_db=0)
	CONFIG = redis_service.hget_redis('config', 'app')
	share_reward = CONFIG['ShareReward']
	if user_id not in users:
		try:
			pre1_info = dnk_db.find_one({'own_code': invite_code})  # 三级代理
			pre1_user_id = pre1_info['user_id']
			pre2_code = pre1_info['pre1_code']
			asset_db.update_one({'user_id': pre1_user_id}, {'asset.share': share_reward * CONFIG['Level3Reward']})
			try:
				pre2_info = dnk_db.find_one({'own_code': pre2_code})    # 二级代理
				pre2_user_id = pre2_info['user_id']
				asset_db.update_one({'user_id': pre2_user_id}, {'asset.share': share_reward * CONFIG['Level2Reward']})
				pre3_code = pre2_info['pre1_code']
				pre3_info = dnk_db.find_one({'own_code': pre3_code})
				pre3_user_id = pre3_info['user_id']
				asset_db.update_one({'user_id': pre3_user_id}, {'asset.share': share_reward * CONFIG['Level1Reward']})
			except Exception as e:
				pre3_code = 'INTIAL'
			try:
				af1_codes = pre1_info['af1_code']
			except Exception as e:
				af1_codes = []
			print(f'af1_codes -> {af1_codes}')
		except Exception as e:
			pre2_code = 'INTIAL'
			af1_codes = []
		dnk_info = {
			'user_id': user_id,
			'own_code': promo_code,
			'pre1_code': invite_code,
			'pre2_code': pre2_code,
			'pre3_code': pre3_code,
			'af1_code': [],
			'af2_code': []
		}
		dnk_db.insert_one_data(dnk_info)
		if invite_code != 'INTIAL': # 三级代理
			af1_codes.append(promo_code)
			dnk_db.update_one({'own_code': invite_code}, {'af1_code': af1_codes})
		if pre2_code != 'INTIAL':   # 二级代理
			af2_codes = dnk_db.collection.update_one({'own_code': pre2_code}, {'$push': {'af2_code': promo_code}},upsert=True)
			# dnk_db.update_one({'own_code': pre2_code}, {'af2_code': af2_codes})
