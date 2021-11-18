from fastapi import APIRouter, Depends, UploadFile, File
from io import BytesIO
from utils.services.base.base_func import *
from utils.services.redis_db_connect.connect import *
from web.models.appminer_models import *

# logger.add(sink='logs/app_miner.log',
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
redis_service = redis_connection(redis_db=0)

@logger.catch(level='ERROR')
@router.post('/all')
async def get_all_miners(get_info: GetAllMiners):
	miners = []
	pref = (get_info.page - 1) * get_info.size
	af = get_info.size
	all_miners = miner_db.collection.find({}, {"_id": 0}).skip(pref).limit(af)
	for miner in all_miners:
		miner_sum_count = redis_service.hget_redis('config', 'app').get(miner['miner_name'], redis_service.hget_redis('config', 'app')['MinerSumCount'])
		miner_numbers = miner.get('miner_numbers', miner_sum_count)
		user_info = {
			'miner_name': miner['miner_name'],
			'miner_month_reward': miner['miner_month_reward'],
			'miner_power': miner['miner_power'],
			'miner_price': miner['miner_price'],
			'miner_team_price': miner['miner_team_price'],
			'miner_manage_price': miner['miner_manage_price'],
			'miner_numbers': miner_numbers,
			'miner_sum_count': miner_sum_count,
			'miner_sale_count': miner_sum_count - miner_numbers
		}
		miners.append(user_info)
		if 'miner_numbers' not in miner.keys():
			miner_db.update_one({'miner_name': miner['miner_name']}, {'miner_numbers': miner_sum_count})
	total_count = miner_db.collection.find({}, {"_id": 0}).count()
	page_tmp = total_count % af
	if page_tmp != 0:
		all_pages = (total_count // af) + 1
	else:
		all_pages = total_count // af
	rep_data = {'filter_count': len(miners), 'record': miners, 'total_count': total_count, 'total_pages': all_pages}
	return msg(status='susscss', data=rep_data)

@logger.catch(level='ERROR')
@router.get('/{miner_name}')
async def get_one_miner(miner_name):
	config = redis_service.hget_redis('config', 'app')
	miner_sum_count = config.get(miner_name, config['MinerSumCount'])
	miner_info = miner_db.find_one({'miner_name': miner_name})
	miner_pic = miner_pic_db.find_one({'user_id': miner_info['miner_name']})['img']
	miner_info['miner_sum_count'] = miner_sum_count
	if 'miner_numbers' not in miner_info.keys():
		miner_info['miner_numbers'] = miner_sum_count
	miner_info['miner_sale_count'] = miner_sum_count - miner_info.get('miner_numbers', miner_sum_count)
	miner_info['img'] = miner_pic
	return msg(status='success', data=miner_info)

@logger.catch(level='ERROR')
@router.post('/add_miner')
async def add_new_miner(add_info: AddMiner):
	miner_info = dict(add_info)
	miner_sum_count = miner_info['miner_sum_count']
	del miner_info['miner_sum_count']
	miner_info['miner_numbers'] = miner_sum_count
	miner_db.insert_one_data(miner_info)
	config = redis_service.hget_redis('config', 'app')
	config[add_info.miner_name] = miner_sum_count
	redis_service.hset_redis('config', 'app', json.dumps(config, ensure_ascii=False))
	return msg(status='success', data='Add new miner successfully')

@logger.catch(level='ERROR')
@router.post('/add_miner_pic')
async def add_miner_pic(file: UploadFile = File(...)):
	miner_pic = await file.read()
	miner_name = file.filename.split('.')[0]
	miner_pic_db.save_img(user_id=miner_name, img=BytesIO(miner_pic))
	return msg(status='success', data='Add miner picture successfully')

@logger.catch(level='ERROR')
@router.post('/update_miner')
async def update_miner(update_info: UpdateMiner):
	miner_name = update_info.miner_name
	miner_info = dict(update_info)
	del miner_info['miner_name']
	updates = {}
	del miner_info['miner_name']
	del miner_info['new_miner_name']
	for inx, (k, v) in enumerate(miner_info.items()):
		if v:
			updates[k] = v
	if update_info.new_miner_name is not None:
		ori_miner_pics = miner_pic_db.find_one({'user_id': update_info.miner_name})['img']
		miner_pic_db.save_img(user_id=update_info.new_miner_name, img=BytesIO(bytes(ori_miner_pics, encoding='utf-8')))
		updates['miner_name'] = update_info.new_miner_name
	miner_db.update_one({'miner_name': miner_name}, updates)
	return msg(status='success', data='Update miner successfully')

@logger.catch(level='ERROR')
@router.post('/delete_miner')
async def delete_miner(delete_info: DeleteMiner):
	miner_db.delete_one({'miner_name': delete_info.miner_name})
	miner_pic_db.delete_one({'user_id': delete_info.miner_name})
	return msg(status='success', data='Delete miner successfully')
