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
