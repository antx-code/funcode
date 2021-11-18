from pydantic import BaseModel
from typing import Optional
from fastapi_users import models

class UserRegister(models.BaseUser):
    email: Optional[str]
    phone: Optional[str]
    password: str
    repassword: str
    nickname: str
    invite_code: str

class UserLogin(models.BaseUser):
    email: Optional[str]
    phone: Optional[str]
    password: str
    phone_code: Optional[str]

class UserLogout(models.BaseUser):
    email: Optional[str]
    phone: Optional[str]

class UserResetPassword(models.BaseUser):
    phone: str
    old_password: Optional[str]
    new_password: str
    new_repassword: str
    verify_code: str

class UserVerify(BaseModel):
    verify_type: str
    phone_email: str
    verify_code: str

class GetVerifyCode(BaseModel):
    verify_type: str
    phone_email: str