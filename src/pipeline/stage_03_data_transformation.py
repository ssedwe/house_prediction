import sys
import os
from src.config.configuration import ConfigurationManager
from src.components.data_transformation import DataTransformation
from src.logger import logger
from src.exception import CustomException

STAGE_NAME = "Data Transformation Stage"

class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            # 1. The Gatekeeper Check
            status_file = "artifacts/data_validation/status.txt"
            
            if not os.path.exists(status_file):
                raise Exception("Validation status file not found. Please run Stage 02 first.")

            with open(status_file, "r") as f:
                # Extracts the 'True' or 'False' from "Validation status: True"
                status = f.read().split(" ")[-1]

            if status != "True":
                raise Exception("Data Validation failed. Pipeline terminating before Transformation.")
            
            # 2. Run Transformation
            logger.info("Validation passed. Initiating Data Transformation...")
            config_manager = ConfigurationManager()
            data_transformation_config = config_manager.get_data_transformation_config()
            
            data_transformation = DataTransformation(config=data_transformation_config)
            data_transformation.initiate_data_transformation()
            
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
        pipeline = DataTransformationTrainingPipeline()
        pipeline.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} completed successfully <<<<<<\n\nx==========x")
    except Exception as e:
        logger.error(e)
        raise CustomException(e, sys)