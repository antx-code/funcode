from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# RunIt API
from api.token import router as token_router
from api.is_alive import router as alive_router
from api.task import router as task_router

from utils.exceptions.customs import InvalidPermissions, UnauthorizedAPIRequest, RecordNotFound, InvalidAPIRequest, ServerError, DatabaseError, InvalidContentType, RecordAlreadyExists


@logger.catch(level='ERROR')
def generate_application() -> FastAPI:
    application = FastAPI(title='RunIt API', version='v1', description='Created by antx at 2021-11-18.', docs_url=None, redoc_url=None)
    application.debug = False

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception(application)

    application.include_router(
        token_router,
        prefix="/api",
        tags=["RunIt generate token API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        alive_router,
        prefix="/api",
        tags=["RunIt is_alive API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        task_router,
        prefix="/api",
        tags=["RunIt task_create API"],
        responses={404: {"description": "Not found"}}
    )

    return application

@logger.catch(level='ERROR')
def register_exception(app: FastAPI):
    """
    全局异常捕获
    注意 别手误多敲一个s
    exception_handler
    exception_handlers
    两者有区别
        如果只捕获一个异常 启动会报错
        @exception_handlers(UserNotFound)
    TypeError: 'dict' object is not callable
    :param app:
    :return:
    """

    @app.exception_handler(InvalidPermissions)
    async def request_validation_exception_handler(request: Request, exc: InvalidPermissions):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(UnauthorizedAPIRequest)
    async def request_validation_exception_handler(request: Request, exc: UnauthorizedAPIRequest):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RecordNotFound)
    async def request_validation_exception_handler(request: Request, exc: RecordNotFound):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RecordAlreadyExists)
    async def request_validation_exception_handler(request: Request, exc: RecordAlreadyExists):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(InvalidAPIRequest)
    async def request_validation_exception_handler(request: Request, exc: InvalidAPIRequest):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(ServerError)
    async def request_validation_exception_handler(request: Request, exc: ServerError):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(DatabaseError)
    async def request_validation_exception_handler(request: Request, exc: DatabaseError):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(InvalidContentType)
    async def request_validation_exception_handler(request: Request, exc: InvalidContentType):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    # 捕获全部异常
    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        全局所有异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=500, content='Unknown Error!')

app = generate_application()
