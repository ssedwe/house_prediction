from backend.src.constants import *
from backend.src.utils.common import read_yaml, create_directories
from backend.src.entity.config_entity import (DataIngestionConfig, 
                                      DataValidationConfig, 
                                      DataTransformationConfig,
                                      ModelTrainerConfig,
                                      ModelEvaluationConfig)
from pathlib import Path

class ConfigurationManager:
    # --- CHANGE 1: Update init to read params and schema ---
    def __init__(
        self, 
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH,
        schema_filepath = SCHEMA_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion
        create_directories([config.artifact_dir])

        data_ingestion_config = DataIngestionConfig(
            database_name=config.database_name,
            collection_name=config.collection_name,
            artifact_dir=Path(config.artifact_dir),
            raw_data_path=Path(config.raw_data_path),
            train_data_path=Path(config.train_data_path),
            test_data_path=Path(config.test_data_path),
            test_size=config.test_size
        )
        return data_ingestion_config
    
    
    
    
    
    
    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        create_directories([config.artifact_dir])

        data_validation_config = DataValidationConfig(
            artifact_dir=Path(config.artifact_dir),
            raw_data_path=Path(config.raw_data_path),
            schema_file_path=Path(config.schema_file_path)
        )
        return data_validation_config
    
    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        
        create_directories([config.artifact_dir])

        data_transformation_config = DataTransformationConfig(
            artifact_dir=Path(config.artifact_dir),
            train_data_path=Path(config.train_data_path),
            test_data_path=Path(config.test_data_path),
            preprocessor_obj_file_path=Path(config.preprocessor_obj_file_path)
        )
        return data_transformation_config

    # --- CHANGE 2: Add the Model Trainer config method ---
   
   
   
   
   
   
    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer
        schema =  self.schema.TARGET_COLUMN

        create_directories([config.artifact_dir])

        model_trainer_config = ModelTrainerConfig(
            artifact_dir=config.artifact_dir,
            train_data_path=config.train_data_path,
            test_data_path=config.test_data_path,
            model_name=config.model_name,
            
            # We pass the word "price" to the trainer
            target_column=schema.name 
        )

        return model_trainer_config
    




    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        config = self.config.model_evaluation
        schema =  self.schema.TARGET_COLUMN

        # Create the model_evaluation folder so the metrics.json has a place to live
        create_directories([config.root_dir])

        model_evaluation_config = ModelEvaluationConfig(
            root_dir=Path(config.root_dir),
            test_data_path=Path(config.test_data_path),
            model_path=Path(config.model_path),
            preprocessor_path=Path(config.preprocessor_path),
            metric_file_name=Path(config.metric_file_name),
            target_column=schema.name
        )

        return model_evaluation_config