from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from utils.exceptions.customs import InvalidPermissions, UnauthorizedAPIRequest, RecordNotFound, InvalidAPIRequest, ServerError, DatabaseError, InvalidContentType, RecordAlreadyExists
from fastapi.responses import JSONResponse
from loguru import logger
# 手机端接口
from app.api.user import router as user_router
from app.api.user_info import router as user_info_router
from app.api.team import router as team_router
from app.api.reward import router as reward_router
from app.api.customer_services import router as csc_router
from app.api.exchange import router as exchange_router
# 后台管理接口
from web.api.admin import router as admin_router
from web.api.app_user import router as appuser_router
from web.api.app_miner import router as appminer_router
from web.api.app_record import router as apprecord_router
from web.api.app_article import router as apparticle_router
from web.api.privilege import router as privilege_router
from web.api.rw_management import router as rwm_router

@logger.catch(level='ERROR')
def generate_application() -> FastAPI:
    application = FastAPI(title='BC-APP-API', version='v1', description='Created by antx at 2021-06-04.', redoc_url=None)
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
        user_router,
        prefix="/api/app/user",
        tags=["APP-USER API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        user_info_router,
        prefix="/api/app/user_info",
        tags=["APP-USER-INFO API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        team_router,
        prefix="/api/app/team",
        tags=["APP-TEAM API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        reward_router,
        prefix="/api/app/reward",
        tags=["APP-REWARD API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        csc_router,
        prefix="/api/app/csc",
        tags=["APP-CustomerServiceCenter API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        exchange_router,
        prefix="/api/app/exchange",
        tags=["APP-EXCHANGE API"],
        responses={404: {"description": "Not found"}}
    )

# ************************* 后台管理功能分界线 ******************************

    application.include_router(
        admin_router,
        prefix="/api/web/admin",
        tags=["BC-ADMIN API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        appuser_router,
        prefix="/api/web/app_user",
        tags=["BC-APPUSER API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        appminer_router,
        prefix="/api/web/app_miner",
        tags=["BC-APPMINER API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        apprecord_router,
        prefix="/api/web/app_record",
        tags=["BC-APPRECORD API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        apparticle_router,
        prefix="/api/web/app_article",
        tags=["BC-APPARTICLE API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        privilege_router,
        prefix="/api/web/privilege",
        tags=["BC-APPPRIVILEGE API"],
        responses={404: {"description": "Not found"}}
    )

    application.include_router(
        rwm_router,
        prefix="/api/web/rwm",
        tags=["BC-APPPRWMANAGEMENT API"],
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
    async def request_InvalidPermissions_exception_handler(request: Request, exc: InvalidPermissions):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(UnauthorizedAPIRequest)
    async def request_UnauthorizedAPIRequest_exception_handler(request: Request, exc: UnauthorizedAPIRequest):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RecordNotFound)
    async def request_RecordNotFound_exception_handler(request: Request, exc: RecordNotFound):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RecordAlreadyExists)
    async def request_RecordAlreadyExists_exception_handler(request: Request, exc: RecordAlreadyExists):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(InvalidAPIRequest)
    async def request_InvalidAPIRequest_exception_handler(request: Request, exc: InvalidAPIRequest):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(ServerError)
    async def request_ServerError_exception_handler(request: Request, exc: ServerError):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(DatabaseError)
    async def request_DatabaseError_exception_handler(request: Request, exc: DatabaseError):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(InvalidContentType)
    async def request_InvalidContentType_exception_handler(request: Request, exc: InvalidContentType):
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