import sys
from src.config.configuration import ConfigurationManager
from src.components.model_trainer import ModelTrainer
from src.logger import logger
from src.exception import CustomException

STAGE_NAME = "Model Training Stage"

class ModelTrainerTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            config_manager = ConfigurationManager()
            model_trainer_config = config_manager.get_model_trainer_config()
            
            model_trainer_obj = ModelTrainer(config=model_trainer_config)
            model_trainer_obj.train()
            
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == '__main__':
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
        pipeline = ModelTrainerTrainingPipeline()
        pipeline.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} completed successfully <<<<<<\n\nx==========x")
    except Exception as e:
        logger.error(e)
        raise CustomException(e, sys)