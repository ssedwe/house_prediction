import os
import sys
import pandas as pd
import joblib
import mlflow
from dotenv import load_dotenv
import mlflow.sklearn
from pathlib import Path
from backend.src.components.data_transformation import FeatureEngineeringWrapper

# Advanced Scikit-Learn Tools
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from backend.src.logger import logger
from backend.src.exception import CustomException
from backend.src.entity.config_entity import ModelTrainerConfig
from backend.src.utils.common import read_yaml

load_dotenv()

class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        try:
            logger.info("Loading raw training and testing data")
            train_data = pd.read_csv(self.config.train_data_path)
            test_data = pd.read_csv(self.config.test_data_path)

            train_data.dropna(inplace=True)
            test_data.dropna(inplace=True)

            logger.info("Separating independent (X) and dependent (y) features")
            # Raw data - NO transformation yet
            train_x = train_data.drop([self.config.target_column], axis=1)
            train_y = train_data[self.config.target_column]
            test_x = test_data.drop([self.config.target_column], axis=1)
            test_y = test_data[self.config.target_column]

            logger.info("Loading smart preprocessor")
            preprocessor_path = "artifacts/data_transformation/preprocessor.pkl"
            preprocessor = joblib.load(preprocessor_path)

            models = {
                "RandomForestRegressor": RandomForestRegressor(),
                "DecisionTreeRegressor": DecisionTreeRegressor(),
                "GradientBoostingRegressor": GradientBoostingRegressor()
            }

            logger.info("Reading params.yaml for GridSearch boundaries")
            params = read_yaml(Path("params.yaml"))

            # MLflow setup
            mlflow.set_tracking_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")
            mlflow.set_registry_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")
            mlflow.set_experiment("House_Price_Prediction_1")  # Emojis removed to prevent Windows crash
            mlflow.sklearn.autolog()

            best_model_score = -float("inf")
            best_model_name = None
            best_model_object = None

            for model_name, model in models.items():
                logger.info(f"Starting Hyperparameter Tuning for {model_name}")

                # 1. CREATE UNIFIED PIPELINE
                pipeline = Pipeline(steps=[
                    ("preprocessor", preprocessor),
                    ("model", model)
                ])

                # 2. MAP PARAMETERS TO THE PIPELINE
                original_param_grid = dict(params[model_name])
                param_grid = {f"model__{k}": v for k, v in original_param_grid.items()}

                with mlflow.start_run(run_name=f"Tuning_{model_name}"):
                    # 3. FIT PIPELINE ON RAW DATA (train_x)
                    gs = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, scoring='r2')
                    gs.fit(train_x, train_y)

                    best_model = gs.best_estimator_

                    # 4. PREDICT ON RAW DATA (test_x)
                    y_pred = best_model.predict(test_x)
                    test_score = r2_score(test_y, y_pred)

                    logger.info(f"{model_name} best R2 score: {test_score}")

                    if test_score > best_model_score:
                        best_model_score = test_score
                        best_model_name = model_name
                        best_model_object = best_model

            logger.info(f"OVERALL CHAMPION: {best_model_name} with R2 Score: {best_model_score}")

            # Register ONLY the unified pipeline to MLflow
            with mlflow.start_run(run_name="Final_Model"):
                mlflow.sklearn.log_model(
                    sk_model=best_model_object,
                    artifact_path="model",
                    registered_model_name="HousePriceModel"
                )
                
                # We NO LONGER log the preprocessor separately
                mlflow.log_metric("best_r2_score", best_model_score)    

            logger.info(f"Champion model registered successfully: {best_model_name}")

            # Promote model to Production stage
            logger.info("Promoting model to Production stage...")
            client = mlflow.tracking.MlflowClient()
            
            latest_versions = client.get_latest_versions("HousePriceModel")
            if latest_versions:
                latest_version = latest_versions[0]
                logger.info(f"Latest model version: {latest_version.version}")
                
                client.transition_model_version_stage(
                    name="HousePriceModel",
                    version=latest_version.version,
                    stage="Production"
                )
                logger.info(f"Model version {latest_version.version} promoted to Production stage successfully!")
            else:
                logger.warning("No model versions found to promote")

        except Exception as e:
            raise CustomException(e, sys)