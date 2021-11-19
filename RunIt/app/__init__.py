from loguru import logger
import yaml

@logger.catch(level='ERROR')
def get_config():
    with open('config.yaml', 'r+', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = get_config()