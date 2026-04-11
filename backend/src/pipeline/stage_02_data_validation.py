import sys
from backend.src.config.configuration import ConfigurationManager
from backend.src.components.data_validation import DataValidation
from backend.src.logger import logger
from backend.src.exception import CustomException
from backend.src.utils.common import read_yaml
from backend.src.constants import SCHEMA_FILE_PATH

STAGE_NAME = "Data Validation Stage"

class DataValidationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            # 1. Get configurations
            config_manager = ConfigurationManager()
            data_validation_config = config_manager.get_data_validation_config()
            
            # 2. Read the schema.yaml file to pass the columns
            schema_dict = read_yaml(SCHEMA_FILE_PATH).COLUMNS 
            
            # 3. Initialize and run component
            data_validation = DataValidation(config=data_validation_config, schema=schema_dict)
            data_validation.initiate_data_validation()
            
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
        pipeline = DataValidationTrainingPipeline()
        pipeline.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} completed successfully <<<<<<\n\nx==========x")
    except Exception as e:
        logger.error(e)
        raise CustomException(e, sys)