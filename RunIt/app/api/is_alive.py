from fastapi import APIRouter, Depends
from utils.services.base.api_base import msg
from handler.create_handler import *
from utils.auth.xauth import verification

router = APIRouter(dependencies=[Depends(verification)])
# router = APIRouter()

@logger.catch(level='ERROR')
@router.get('/is_alive')
async def is_alive():
    return msg(status='success', data='alive')
