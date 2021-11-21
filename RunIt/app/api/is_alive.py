from fastapi import APIRouter, Depends
from utils.services.base.api_base import msg
from utils.xauth.antx_auth import verification
from handler.alive_handler import *

router = APIRouter(dependencies=[Depends(verification)])
# router = APIRouter()

@logger.catch(level='ERROR')
@router.get('/is_alive')
async def is_alive():
    alive_status, message = await aliveH()
    return msg(status=alive_status, data=message)
