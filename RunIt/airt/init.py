from loguru import logger
import yaml
import sys
import os

path = os.getcwd()
sys.path.append(path)

@logger.catch(level='ERROR')
def get_config():
    with open(f'{path}/config.yaml', 'r+', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = get_config()