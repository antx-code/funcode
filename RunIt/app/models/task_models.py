from pydantic import BaseModel
from typing import Optional
import time

class TaskCreate(BaseModel):
    room: str
    task_name: Optional[str] = f'RUNIT-{int(time.time())}'
    mode: str = 'record'

class TaskStop(BaseModel):
    task_id: str
