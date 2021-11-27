from loguru import logger
import yaml
import sys
sys.path.append('/home/antx/Code/tmp/funcode/RunIt/app/')

@logger.catch(level='ERROR')
def get_config():
    with open(f'config.yaml', 'r+', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = get_config()