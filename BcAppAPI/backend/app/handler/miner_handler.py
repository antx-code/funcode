from loguru import logger
from utils.services.base.SnowFlake import IdWorker

id_worker = IdWorker(0, 0)

@logger.catch(level='ERROR')
def generate_miner_id():
	miner_id = str(id_worker.get_id())
	return f'NO.{miner_id[:10]}'