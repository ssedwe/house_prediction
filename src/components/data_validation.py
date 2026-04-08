import os
import sys
import pandas as pd
from src.logger import logger
from src.exception import CustomException
from src.entity.config_entity import DataValidationConfig

class DataValidation:
    def __init__(self, config: DataValidationConfig, schema: dict):
        self.config = config
        self.schema = schema

    def validate_all_columns_exist(self) -> bool:
        """Checks if all columns defined in schema.yaml exist in the dataframe."""
        try:
            validation_status = True
            
            # Read the raw ingested data (or you could read train.csv)
            df = pd.read_csv(self.config.raw_data_path)
            all_cols = list(df.columns)
            
            # Get the expected columns from schema.yaml
            expected_cols = list(self.schema.keys())

            for col in expected_cols:
                if col not in all_cols:
                    validation_status = False
                    logger.error(f"Validation Failed: Column '{col}' is missing from the dataset.")
                    break # Stop checking if one is missing to save computation
            
            if validation_status:
                logger.info("All expected columns found in the dataset.")

            # Create artifact directory if it doesn't exist
            os.makedirs(self.config.artifact_dir, exist_ok=True)
            
            # Write the status to a text file for the pipeline to read later
            status_file_path = os.path.join(self.config.artifact_dir, "status.txt")
            with open(status_file_path, 'w') as f:
                f.write(f"Validation status: {validation_status}")
                
            return validation_status
            
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_validation(self) -> bool:
        """Executes the validation process."""
        try:
            logger.info("Starting Data Validation")
            status = self.validate_all_columns_exist()
            logger.info(f"Data Validation completed. Status: {status}")
            return status

        except Exception as e:
            raise CustomException(e, sys)