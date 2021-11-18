from pydantic import BaseModel
from typing import Optional

class AllRecords(BaseModel):
    page: int
    size: int

class GetRecord(BaseModel):
    page: int
    size: int
    type: str
    user_id: str