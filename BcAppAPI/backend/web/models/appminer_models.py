from pydantic import BaseModel
from typing import Optional

class GetAllMiners(BaseModel):
    page: int
    size: int

class AddMiner(BaseModel):
	miner_name: str
	miner_month_reward: float
	miner_power: str
	miner_price: float
	miner_team_price: float
	miner_manage_price: float
	miner_sum_count: int

class UpdateInfo(BaseModel):
    pass

class UpdateMiner(BaseModel):
    miner_name: str
    new_miner_name: Optional[str]
    miner_month_reward: Optional[float]
    miner_power: Optional[str]
    miner_price: Optional[float]
    miner_team_price: Optional[float]
    miner_manage_price: Optional[float]
    miner_sum_count: Optional[int]

class DeleteMiner(BaseModel):
    miner_name: str
