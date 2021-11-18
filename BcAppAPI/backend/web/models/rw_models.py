from pydantic import BaseModel
from typing import Optional

class GetAllRw(BaseModel):
    page: int
    size: int
    type: str

class GetOneRw(BaseModel):
    record_id: str

class UpdateOneRw(BaseModel):
    record_id: str
    status: str
