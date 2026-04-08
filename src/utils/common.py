import os
import sys
import json
import yaml
from pathlib import Path  # <--- The missing puzzle piece!
from box import ConfigBox

from src.logger import logging
from src.exception import CustomException

def read_yaml(path_to_yaml):
    with open(path_to_yaml) as yaml_file:
        content = yaml.safe_load(yaml_file)
        return ConfigBox(content)   # 🔥 IMPORTANT

def create_directories(paths: list):
    try:
        for path in paths:
            os.makedirs(path, exist_ok=True)
            logging.info(f"Directory created or already exists: {path}")
    except Exception as e:
        raise CustomException(e, sys)

def save_json(path: Path, data: dict):
    """
    Saves dictionary data to a JSON file.
    
    Args:
        path (Path): path to json file
        data (dict): data to be saved in json file
    """
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
            
        logging.info(f"JSON file successfully saved at: {path}")
        
    except Exception as e:
        raise CustomException(e, sys)