from pydantic import BaseModel
from typing import Optional

class GetAllUsers(BaseModel):
    page: int
    size: int

class AddUser(BaseModel):
    email: Optional[str] = ''
    phone: Optional[str] = ''
    nickname: str
    init_password: str = '123456789'

class UpdateInfo(BaseModel):
    nickname: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    reset_password: Optional[bool]
    is_logged_in: Optional[bool]
    is_active: Optional[bool]
    is_verified: Optional[bool]
    member_status: Optional[str]
    level_status: Optional[str]

class UpdateUser(BaseModel):
    user_id: str
    update_info: UpdateInfo

class DeleteUser(BaseModel):
    user_id: str
