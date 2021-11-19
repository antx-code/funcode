from fastapi import APIRouter, Depends
from loguru import logger
from utils.services.base.api_base import msg
from handler.create_handler import *
from utils.xauth.antx_auth import verification

router = APIRouter(dependencies=[Depends(verification)])
# router = APIRouter()

@logger.catch(level='ERROR')
@router.get('/is_alive')
async def is_alive():
    return msg(status='success', data='alive')