from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

@logger.catch(level='ERROR')
def msg(status, data, code=None):
    if code:
        final_data = {'status': status, 'code': code, 'data':data}
    else:
        final_data = {'data':data, 'msg':status}
    return JSONResponse(content=jsonable_encoder(final_data))
