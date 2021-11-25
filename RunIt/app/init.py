from loguru import logger
import yaml
import os

@logger.catch(level='ERROR')
def get_config():
    with open(f'/Users/antx/Code/funcode/RunIt/app/config.yaml', 'r+', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = get_config()