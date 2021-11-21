from fastapi import APIRouter
from utils.services.base.api_base import msg
from handler.token_handler import *
from models.token_models import *

router = APIRouter()

@logger.catch(level='ERROR')
@router.post('/token')
async def generate_token(token_info: GeToken):
    token = create_authtoken(token_info.identity)
    return msg(status='success', data=token)
