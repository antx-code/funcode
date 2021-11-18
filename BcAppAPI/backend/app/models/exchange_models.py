from pydantic import BaseModel
from typing import Optional, List

class BuyMiner(BaseModel):
	miner_name: str
	miner_price: float

class TeamBuyMiner(BaseModel):
	miner_name: str
	miner_sum_price: float
	miner_per_price: float
	share_buy_code: str

class RecordInfo(BaseModel):
	record_type: str
	record_scope: dict

class RechargeInfo(BaseModel):
	recharge_usdt: float

class WithdrawInfo(BaseModel):
	withdraw_usdt: float

class ShareBuy(BaseModel):
	miner_name: str

class PostNotice(BaseModel):
	phone: Optional[str]
	email: Optional[str]
	miner_name: str
