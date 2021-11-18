from loguru import logger
from pydantic import BaseModel
from typing import Optional

class SetupProfile(BaseModel):
	nickname: Optional[str]
	sex: Optional[str] = 'male'
	area: Optional[str] = "china"
	intro: Optional[str] = "这个家伙很懒，什么都没留下"

class WithdrawAddress(BaseModel):
	address: str
