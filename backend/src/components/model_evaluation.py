import os
import sys
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from urllib.parse import urlparse
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from backend.src.logger import logger
from backend.src.exception import CustomException
from backend.src.entity.config_entity import ModelEvaluationConfig
from backend.src.utils.common import save_json
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path
# CRITICAL MLOPS IMPORT: We must import the custom wrapper so joblib can unpickle it!
from backend.src.components.data_transformation import FeatureEngineeringWrapper
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
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
            logger.info("Loading unseen test data")
            test_data = pd.read_csv(self.config.test_data_path)
            
            # Drop missing values to match training logic
            test_data.dropna(inplace=True)

            # Separate X and y
            test_x = test_data.drop([self.config.target_column], axis=1)
            test_y = test_data[[self.config.target_column]]

            logger.info("Loading smart preprocessor and trained model")
            preprocessor = joblib.load(self.config.preprocessor_path)
            model = joblib.load(self.config.model_path)

            # ====================================================
            # THE MAGIC: One line does the Pandas math AND the scaling!
            # ====================================================
            logger.info("Transforming test data using smart preprocessor")
            test_x_transformed = preprocessor.transform(test_x)
            # ====================================================

            # Set MLflow tracking URI (Connects to DagsHub)
            mlflow.set_registry_uri("https://dagshub.com/ssedwe/house_prediction.mlflow") 
            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

            with mlflow.start_run():
                logger.info("Making predictions on transformed test data")
                predicted_qualities = model.predict(test_x_transformed)

                logger.info("Calculating metrics")
                (rmse, mae, r2) = self.eval_metrics(test_y, predicted_qualities)
                
                # Saving metrics locally
                scores = {"rmse": rmse, "mae": mae, "r2": r2}
                save_json(path=Path(self.config.metric_file_name), data=scores)

                # Logging metrics to the MLflow Cloud
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("mae", mae)
                mlflow.log_metric("r2", r2)

                # Logging the actual model to the MLflow Vault
                if tracking_url_type_store != "file":
                    mlflow.sklearn.log_model(model, "model", registered_model_name="LinearRegressionModel")
                else:
                    mlflow.sklearn.log_model(model, "model")
                    
            logger.info("Model Evaluation completed and logged to MLflow successfully!")

        except Exception as e:
            raise CustomException(e, sys)