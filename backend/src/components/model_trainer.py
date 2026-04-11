import os
import sys
import pandas as pd
import joblib
import mlflow
import mlflow.sklearn
from pathlib import Path
from backend.src.components.data_transformation import FeatureEngineeringWrapper

# Advanced Scikit-Learn Tools
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

from backend.src.logger import logger
from backend.src.exception import CustomException
from backend.src.entity.config_entity import ModelTrainerConfig
from backend.src.utils.common import read_yaml

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
            # We use 1D Series for y to prevent Scikit-Learn warnings
            train_x = train_data.drop([self.config.target_column], axis=1)
            train_y = train_data[self.config.target_column]
            test_x = test_data.drop([self.config.target_column], axis=1)
            test_y = test_data[self.config.target_column]

            logger.info("Loading smart preprocessor")
            preprocessor_path = "artifacts/data_transformation/preprocessor.pkl"
            preprocessor = joblib.load(preprocessor_path)

            logger.info("Transforming the data...")
            X_train = preprocessor.transform(train_x)
            X_test = preprocessor.transform(test_x)

            # ==============================================================
            # 1. THE DYNAMIC DICTIONARY MATCHER
            # If you ever want to add XGBoost next month, you just add it here 
            # and to params.yaml. The code handles the rest automatically!
            # ==============================================================
            models = {
                "RandomForestRegressor": RandomForestRegressor(),
                "DecisionTreeRegressor": DecisionTreeRegressor(),
                "GradientBoostingRegressor": GradientBoostingRegressor()
            }

            logger.info("Reading params.yaml for GridSearch boundaries")
            params = read_yaml(Path("params.yaml"))

            # ==============================================================
            # 2. THE MLFLOW AUTOLOGGER (The Magic Security Camera)
            # ==============================================================
            mlflow.set_registry_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")
            mlflow.sklearn.autolog() # Automatically tracks all 42 combinations!

            best_model_score = -float("inf")
            best_model_name = None
            best_model_object = None

            # Loop through our dictionary of models
            for model_name, model in models.items():
                logger.info(f"Starting Hyperparameter Tuning for {model_name}")

                # Grab the specific parameters for this model from params.yaml
                param_grid = dict(params[model_name])

                # Create a parent MLflow run for each algorithm
                with mlflow.start_run(run_name=f"Tuning_{model_name}"):
                    
                    # Run GridSearch (Tests all parameter combinations automatically)
                    gs = GridSearchCV(model, param_grid, cv=3, n_jobs=-1, scoring='r2')
                    gs.fit(X_train, train_y)

                    # Extract the absolute best version of THIS specific algorithm
                    best_model = gs.best_estimator_

                    # Test it on the unseen testing data to see how it performs in reality
                    y_pred = best_model.predict(X_test)
                    test_score = r2_score(test_y, y_pred)

                    logger.info(f"{model_name} best R2 score: {test_score}")

                    # If this is the highest score we've seen overall, crown it the new Champion!
                    if test_score > best_model_score:
                        best_model_score = test_score
                        best_model_name = model_name
                        best_model_object = best_model

            logger.info(f"🏆 OVERALL CHAMPION: {best_model_name} with R2 Score: {best_model_score}")

            # ==============================================================
            # 3. SAVE THE CHAMPION
            # We ONLY save the absolute best model to the hard drive.
            # Stage 05 will pick this up and register it to the Production Cloud!
            # ==============================================================
            model_path = os.path.join(self.config.artifact_dir, self.config.model_name)
            joblib.dump(best_model_object, model_path)
            logger.info(f"Champion model saved successfully at {model_path}")

        except Exception as e:
            raise CustomException(e, sys)