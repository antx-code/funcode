from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

@logger.catch(level='ERROR')
def msg(status, data, code=None):
    if not code:
        final_data = {'data': data, 'msg': status}
    else:
        final_data = {'status': status, 'code': code, 'data': data}
    return JSONResponse(content=jsonable_encoder(final_data))
