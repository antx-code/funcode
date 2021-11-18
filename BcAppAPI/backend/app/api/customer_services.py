from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from loguru import logger
import json
import time
from io import BytesIO
from utils.services.base.base_func import *
from utils.services.redis_db_connect.connect import *

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

announcement_db = db_connection('bc-app', 'announcement')
cs_db = db_connection('bc-app', 'customer_urls')

@logger.catch(level='ERROR')
@router.get('/announcement/list')
async def get_announcement_list():
	alist = []
	all_announcement = announcement_db.query_data({})
	for adb in all_announcement:
		alist.append({'aid': adb['aid'], 'title': adb['title']})
	return alist

@logger.catch(level='ERROR')
@router.get('/announcement/{announcement_id}')
async def get_announcement_detail(announcement_id):
	return announcement_db.find_one({'aid': announcement_id})

@logger.catch(level='ERROR')
@router.get('/customer_urls')
async def get_customer_urls():
	cs_urls = []
	results = cs_db.query_data()
	for url in results:
		logger.info(url)
		cs_urls.append(url['url'])
	return msg(status='success', data=cs_urls)
