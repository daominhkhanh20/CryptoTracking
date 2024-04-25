import json
import logging
import yaml

logger = logging.getLogger(__name__)


def load_yaml_file(path_file: str):
    with open(path_file) as file:
        data = yaml.load(file, Loader=yaml.loader.SafeLoader)
    return data


def load_json_file(path_file: str):
    with open(path_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # logger.info(f"Load json data at: {path_file}")
    return data

def write_json(data, path_file):
    with open(path_file, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    # logger.info(f"Save json done at {path_file}")
