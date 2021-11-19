from fastapi import APIRouter, Depends
from loguru import logger
from utils.services.base.api_base import msg
from utils.xauth.antx_auth import verification
from handler.alive_handler import *

router = APIRouter(dependencies=[Depends(verification)])
# router = APIRouter()

@logger.catch(level='ERROR')
@router.get('/is_alive')
async def is_alive():
    return msg(status='success', data='alive')
