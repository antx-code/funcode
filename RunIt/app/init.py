from loguru import logger
import yaml
import sys
import os

path = os.getcwd()
sys.path.append(f'{path}/RunIt/app/')

@logger.catch(level='ERROR')
def get_config():
    with open(f'config.yaml', 'r+', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = get_config()