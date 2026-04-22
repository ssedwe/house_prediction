import os
import sys
import pandas as pd
import numpy as np
import mlflow
import mlflow.pyfunc  # Use pyfunc for universal loading
from urllib.parse import urlparse
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from backend.src.logger import logger
from backend.src.exception import CustomException
from backend.src.entity.config_entity import ModelEvaluationConfig
from backend.src.utils.common import save_json
from pathlib import Path
from dotenv import load_dotenv

# Note: joblib and FeatureEngineeringWrapper imports are removed because 
# the Unified Pipeline handles everything internally now.

class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        return rmse, mae, r2

    def log_into_mlflow(self):
        try:
            logger.info("Loading unseen RAW test data")
            test_data = pd.read_csv(self.config.test_data_path)
            test_data.dropna(inplace=True)

            # Separate X and y
            test_x = test_data.drop([self.config.target_column], axis=1)
            test_y = test_data[[self.config.target_column]]

            # Set MLflow environment
            mlflow.set_tracking_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")
            mlflow.set_registry_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")
            
            # Load the Unified Pipeline (Brain + Translator combined)
            logger.info("Fetching Unified Champion model from MLflow registry...")
            
            # Use pyfunc.load_model for the most stable cross-environment loading
            model = mlflow.pyfunc.load_model("models:/HousePriceModel/Production")
            logger.info("Champion model loaded successfully")

            # ====================================================
            # NO MANUAL TRANSFORMATION HERE! 
            # The model is a Pipeline; it transforms the data itself.
            # ====================================================

            with mlflow.start_run(run_name="Model_Evaluation"):
                logger.info("Making predictions on RAW test data")
                # We pass RAW test_x directly
                predicted_qualities = model.predict(test_x)

                logger.info("Calculating evaluation metrics")
                (rmse, mae, r2) = self.eval_metrics(test_y, predicted_qualities)
                
                # Saving metrics locally
                scores = {"rmse": rmse, "mae": mae, "r2": r2}
                save_json(path=Path(self.config.metric_file_name), data=scores)
                logger.info(f"Metrics saved locally - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")

                # Logging metrics to MLflow Cloud
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("mae", mae)
                mlflow.log_metric("r2", r2)
                logger.info("Evaluation metrics logged to MLflow")
                    
            logger.info("Model Evaluation completed successfully!")

        except Exception as e:
            # Emojis removed to prevent Windows terminal crashes
            logger.error(f"Model Evaluation failed: {e}")
            raise CustomException(e, sys)