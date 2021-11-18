from pydantic import BaseModel
from typing import Optional

class MyMinerDetail(BaseModel):
	miner_id: str
	miner_name: str
	miner_type: str

class MinerRewardRecord(BaseModel):
	record_type: str
	record_scope: dict
