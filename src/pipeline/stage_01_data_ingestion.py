import sys
from src.logger import logger
from src.exception import CustomException
from src.config.configuration import ConfigurationManager
from src.components.data_ingestion import DataIngestion

STAGE_NAME = "Data Ingestion Stage"

class DataIngestionTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config_manager = ConfigurationManager()
            data_ingestion_config = config_manager.get_data_ingestion_config()
            data_ingestion = DataIngestion(config=data_ingestion_config)
            data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
        pipeline = DataIngestionTrainingPipeline()
        pipeline.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} completed successfully <<<<<<\n\nx==========x")
    except Exception as e:
        logger.error(e)
        raise CustomException(e, sys)