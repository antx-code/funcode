from pydantic import BaseModel
from typing import Optional
import time

class TaskLists(BaseModel):
    page: int
    size: int

class TaskCreate(BaseModel):
    room: int
    task_name: Optional[str] = f'RUNIT-{int(time.time())}'
    mode: str = 'record'

class TaskStopDelete(BaseModel):
    task_id: str

class PokerModel(BaseModel):
    head: Optional[list] = [None, None, None]
    mid: Optional[list] = [None, None, None, None, None]
    tail: Optional[list] = [None, None, None, None, None]
    drop: Optional[list] = [None, None, None, None]

class RecordModel(BaseModel):
    local: PokerModel
    player1: PokerModel
    player1: Optional[PokerModel]

class AppStorageRecord(BaseModel):
    task_id: str
    room: int
    status: str
    record: dict
