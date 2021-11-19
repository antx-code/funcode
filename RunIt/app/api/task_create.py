from fastapi import APIRouter, Depends
from loguru import logger
from utils.services.base.api_base import msg
from utils.xauth.antx_auth import verification
from handler.create_handler import *
from models.task_models import TaskCreate

router = APIRouter(dependencies=[Depends(verification)])

@logger.catch(level='ERROR')
@router.post('/create')
async def task_create(task_info: TaskCreate):

    return msg(status='success',)
