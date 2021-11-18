from fastapi import APIRouter, Depends, UploadFile, File
from io import BytesIO
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

# router = APIRouter()

user_info_db = db_connection('bc-app', 'user-info')
user_db = db_connection('bc-app', 'users')
avatar_db = db_connection('bc-app', 'avatar')
promo_qrcode_db = db_connection('bc-app', 'promo_qrcode')
asset_db = db_connection('bc-app', 'assets')
address_db = db_connection('bc-app', 'address')
redis_service = redis_connection(redis_db=0)

@logger.catch(level='ERROR')
@router.post('/avatar/upload')
async def avatar_upload(request: Request, file: UploadFile = File(...)):
	user_id = antx_auth(request)
	avatar = await file.read()
	avatar_db.save_img(user_id=user_id, img=BytesIO(avatar), img_name='avatar')
	return msg(status='success', data=f'上传头像成功')


@logger.catch(level='ERROR')
@router.get('/avatar')
async def get_avatar(request: Request):
	user_id = antx_auth(request)
	try:
		avatar = avatar_db.find_one({'user_id': user_id})['avatar']
	except Exception as e:
		avatar = avatar_db.find_one({'user_id': 'default'})['img']
	return msg(status='success', data={'avatar': avatar})

@logger.catch(level='ERROR')
@router.post('/sprofile')
async def setup_profile(request: Request, user_profile: SetupProfile):
	user_id = antx_auth(request)
	nicknames = user_info_db.dep_data('base_info.profile.nickname')
	print(nicknames)
	user_info = user_db.find_one({'user_id': user_id})

	if not user_profile.nickname:
		nickname = user_info['nickname']
	else:
		nickname = user_profile.nickname
		user_db.update_one({'user_id': user_id}, {'nickname': nickname})

	if nickname in nicknames:
		return msg(status='error', data="Nickname was already used!", code=205)

	save_info = {'user_id': user_id, 'base_info':{
		'profile': {
			'nickname': nickname,
			'sex': user_profile.sex,
			'area': user_profile.area,
			'intro': user_profile.intro
		},
		'share':{
			'promo_code': user_info['promo_code'],
		}
	}}
	user_info_db.update_one({'user_id': user_id}, save_info)
	return msg(status="success", data="修改基础信息成功")

@logger.catch(level='ERROR')
@router.get('/gprofile')
async def get_profile(request: Request):
	user_id = antx_auth(request)
	base_info = user_info_db.find_one({'user_id': user_id})['base_info']['profile']
	return msg(status="success", data=base_info)

@logger.catch(level='ERROR')
@router.get('/share')
async def get_promo_code(request: Request):
	user_id = antx_auth(request)
	share_info = promo_qrcode_db.find_one({'user_id': user_id})
	promo_code = share_info['promo_code']
	promo_qrcode = share_info['promo_qrcode']
	share_info = {'promo_code': promo_code, 'qrcode': promo_qrcode}
	return msg(status="success", data=share_info)

@logger.catch(level='ERROR')
@router.get('/simple_info')
async def simple_info(request: Request):
	user_id = antx_auth(request)
	nickname = user_db.find_one({'user_id': user_id})['nickname']
	asset = asset_db.find_one({'user_id': user_id})['asset']['usdt']['all']
	return msg(status='success', data={'nickname': nickname, 'asset': asset})

@logger.catch(level='ERROR')
@router.post('/add_update_address')
async def add_update_address(request: Request, address_info: WithdrawAddress):
	user_id = antx_auth(request)
	address_db.update_one({'user_id': user_id}, {'address': address_info.address})
	return msg(status='success', data=f'Success binding withdraw address: {address_info.address}!')

@logger.catch(level='ERROR')
@router.get('/get_address')
async def get_address(request: Request):
	user_id = antx_auth(request)
	try:
		address = address_db.find_one({'user_id': user_id})['address']
		return msg(status='success', data=address)
	except Exception as e:
		return msg(status='error', data='Unbinding address!', code=210)


@logger.catch(level='ERROR')
@router.get('/delete_address')
async def delete_address(request: Request):
	user_id = antx_auth(request)
	address_db.delete_one({'user_id': user_id})
	return msg(status='success', data='Success unbinding address!')
