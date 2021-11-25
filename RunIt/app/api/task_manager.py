from fastapi import APIRouter, Depends, BackgroundTasks
from utils.services.base.api_base import msg
from utils.xauth.antx_auth import verification
from handler.task_handler import *
from models.task_models import *
from tmp.fake_play import FakePlay

router = APIRouter(dependencies=[Depends(verification)])

@logger.catch(level='ERROR')
@router.post('/tasks')
async def get_all_task(task_info: TaskLists):
    size = task_info.size
    page = (task_info.page - 1) * size
    final_data, total_count = await get_task_list(page, size)
    rep_data = {'filter_count': len(final_data), 'records': final_data, 'total_count': total_count}
    return msg(status='查询成功', data=rep_data)

@logger.catch(level='ERROR')
@router.post('/create')
async def task_create(task_info: TaskCreate, bkb: BackgroundTasks):
    task_id = GeTaskId()
    resp_data = await create_one_task(task_id, task_info.task_name, task_info.room, task_info.mode)
    fp = FakePlay()
    bkb.add_task(fp.fake_plays)
    return msg(status='success', data=resp_data)

@logger.catch(level='ERROR')
@router.get('/status/{task_id}')
async def task_status(task_id):
    resp_data = await get_task_status(task_id)
    return msg(status='success', data=resp_data)

@logger.catch(level='ERROR')
@router.post('/stop')
async def task_stop(task_info: TaskStopDelete):
    resp_data = await stop_one_task(task_info.task_id)
    return msg(status='success', data=resp_data)

@logger.catch(level='ERROR')
@router.post('/delete')
async def task_delete(task_info: TaskStopDelete):
    resp_data = await delete_one_task(task_info.task_id)
    return msg(status='success', data=resp_data)

@logger.catch(level='ERROR')
@router.get('/record/{task_id}')
async def task_record(task_id):
    resp_data = await get_one_record(task_id)
    return msg(status='success', data=resp_data)
