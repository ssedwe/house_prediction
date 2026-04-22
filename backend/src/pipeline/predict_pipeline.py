import os
import sys
import pandas as pd
import joblib
import mlflow
from typing import Union
from dotenv import load_dotenv

from backend.src.components.data_transformation import FeatureEngineeringWrapper 
from backend.src.exception import CustomException
from backend.src.logger import logger
from backend.src.entity.config_entity import PredictionConfig

# ==============================================================
# ENVIRONMENT SETUP (Industry Standard: Dynamic Configuration)
# ==============================================================
load_dotenv()

# We pull credentials safely from the environment. 
os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("DAGSHUB_USERNAME")
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("DAGSHUB_TOKEN")

# We use getenv to allow local testing, but fallback to your DagsHub URL if missing
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/ssedwe/house_prediction.mlflow")
mlflow.set_tracking_uri(TRACKING_URI)

class PredictPipeline:
    """
    Production-ready Prediction Pipeline
    Uses a hybrid approach: Local Preprocessor + Cloud MLflow Model
    """
    def __init__(self, config: PredictionConfig):
        self.config = config

        try:
            # ==============================================================
            # NEW LOGIC: Pull EVERYTHING from the Cloud (Dagshub/MLflow)
            # ==============================================================
            client = mlflow.tracking.MlflowClient()
            
            logger.info("Fetching champion model info from MLflow registry (@production)...")
            # 1. Find out which specific Run ID is currently marked as "Production"
            prod_model = client.get_latest_versions("HousePriceModel", stages=["Production"])[0]
            run_id = prod_model.run_id

            logger.info(f"Downloading preprocessor from MLflow Run ID: {run_id}")
            # 2. Download the preprocessor linked to that exact Run ID
            downloaded_preprocessor_path = mlflow.artifacts.download_artifacts(
                run_id=run_id, 
                artifact_path="preprocessor/preprocessor.pkl"
            )
            # Load it into memory
            self.preprocessor = joblib.load(downloaded_preprocessor_path)

            logger.info("Loading MLflow model into memory...")
            # 3. Load the Cloud Model from MLflow
            self.model = mlflow.pyfunc.load_model("models:/HousePriceModel@production")

            logger.info("✅ ML artifacts (Preprocessor + MLflow Model) loaded successfully from Cloud")

        except Exception as e:
            logger.exception("❌ Failed to load ML artifacts from MLflow")
            raise CustomException(e, sys)

    def predict(self, features: Union[pd.DataFrame, dict]):
        try:
            # ==============================================================
            # 1. Handle input types securely
            # ==============================================================
            if isinstance(features, dict):
                features = pd.DataFrame([features])

            if not isinstance(features, pd.DataFrame):
                raise TypeError("Input must be a dict or pandas DataFrame")

            if features.empty:
                raise ValueError("Input DataFrame is empty")

            # ==============================================================
            # 2. Transform (Apply your custom Feature Engineering locally)
            # ==============================================================
            logger.info("Applying preprocessor transformations...")
            data_scaled = self.preprocessor.transform(features)

            # ==============================================================
            # 3. Predict (Using the dynamically loaded Cloud Model)
            # ==============================================================
            logger.info("Generating predictions...")
            preds = self.model.predict(data_scaled)

            logger.info(f"Prediction successful: {preds}")

            return preds.tolist()

        except Exception as e:
            logger.exception("❌ Error during prediction")
            raise CustomException(e, sys)


# ==============================================================
# SINGLETON INSTANCE (CRITICAL FOR API PERFORMANCE)
# ==============================================================
_predict_pipeline_instance = None

def get_predict_pipeline(config: PredictionConfig) -> PredictPipeline:
    """
    Singleton factory -> Ensures the MLflow model is only downloaded 
    ONCE when your server starts, keeping API response times fast.
    """
    global _predict_pipeline_instance

    if _predict_pipeline_instance is None:
        _predict_pipeline_instance = PredictPipeline(config)

    return _predict_pipeline_instance