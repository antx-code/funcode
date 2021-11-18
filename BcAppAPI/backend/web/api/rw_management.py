from fastapi import APIRouter, Depends
from utils.services.base.base_func import *
from utils.services.redis_db_connect.connect import *
from web.models.rw_models import *

# logger.add(sink='logs/recharge_withdraw_management.log',
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
async def get_record(get_info: GetAllRw):
	records = []
	pref = (get_info.page - 1) * get_info.size
	af = get_info.size
	try:
		record_info = record_db.collection.find({'type': get_info.type, 'status': 'pending'}, {"_id": 0}).skip(pref).limit(af)
		for record in record_info:
			record['record_id'] = str(record['record_id'])
			records.append(record)
	except Exception as e:
		pass
	total_count = record_db.collection.find({'type': get_info.type, 'status': 'pending'}, {"_id": 0}).count()

	page_tmp = total_count % af
	if page_tmp != 0:
		all_pages = (total_count // af) + 1
	else:
		all_pages = total_count // af
	rep_data = {'filter_count': len(records), 'record': records, 'total_count': total_count, 'total_pages': all_pages}
	return msg(status='susscss', data=rep_data)

@logger.catch(level='ERROR')
@router.post('/get_one')
async def get_one(get_info: GetOneRw):
	records = []
	try:
		record_info = record_db.collection.find({'record_id': int(get_info.record_id)}, {"_id": 0})
		for record in record_info:
			record['record_id'] = int(record['record_id'])
			records.append(record)
	except Exception as e:
		pass
	return msg(status='success', data=records)

@logger.catch(level='ERROR')
@router.post('/update_one')
async def update_one(update_info: UpdateOneRw):
	record_db.update_one({'record_id': int(update_info.record_id)}, {'status': update_info.status})
	return msg(status='success', data=f'Verify {update_info.record_id} successfully')

@logger.catch(level='ERROR')
@router.post('/delete_one')
async def delete_one(delete_info: GetOneRw):
	record_db.delete_one({'record_id': int(delete_info.record_id)})
	return msg(status='success', data=f'Delete {delete_info.record_id} successfully')
