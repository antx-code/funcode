from pydantic import BaseModel
from typing import Optional

class PrivilegeList(BaseModel):
    page: int
    size: int
    type: str

class SetPrivilege(BaseModel):
    user_id: str
    privilege: str
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_logged_in: Optional[bool]
