from pydantic import BaseModel
from typing import Optional
import time

class GeToken(BaseModel):
    identity: str
