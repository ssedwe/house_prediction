import sys
import pandas as pd
import joblib
from typing import Union

# Cleaned, single set of imports
from backend.src.components.data_transformation import FeatureEngineeringWrapper 
from backend.src.exception import CustomException
from backend.src.logger import logger
from backend.src.entity.config_entity import PredictionConfig

class PredictPipeline:
    """
    Production-ready Prediction Pipeline
    """
    def __init__(self, config: PredictionConfig):
        self.config = config

        try:
            logger.info(f"Loading preprocessor from: {self.config.preprocessor_path}")
            logger.info(f"Loading model from: {self.config.model_path}")

            # Load ONCE (important)
            self.model = joblib.load(self.config.model_path)
            self.preprocessor = joblib.load(self.config.preprocessor_path)

            logger.info("✅ ML artifacts loaded successfully")

        except Exception as e:
            logger.exception("❌ Failed to load ML artifacts")
            raise CustomException(e, sys)

    def predict(self, features: Union[pd.DataFrame, dict]):
        try:
            # ==============================================================
            # 1. Handle input types (dict or DataFrame)
            # ==============================================================
            if isinstance(features, dict):
                features = pd.DataFrame([features])

            if not isinstance(features, pd.DataFrame):
                raise TypeError("Input must be a dict or pandas DataFrame")

            if features.empty:
                raise ValueError("Input DataFrame is empty")

            # ==============================================================
            # 2. Transform (Passes data directly to your Custom Wrapper)
            # ==============================================================
            data_scaled = self.preprocessor.transform(features)

            # ==============================================================
            # 3. Predict
            # ==============================================================
            preds = self.model.predict(data_scaled)

            logger.info(f"Prediction successful: {preds}")

            return preds.tolist()

        except Exception as e:
            logger.exception("❌ Error during prediction")
            raise CustomException(e, sys)


# ==============================================================
# SINGLETON INSTANCE (VERY IMPORTANT FOR PERFORMANCE)
# ==============================================================
_predict_pipeline_instance = None

def get_predict_pipeline(config: PredictionConfig) -> PredictPipeline:
    """
    Singleton factory → ensures model loads only once
    """
    global _predict_pipeline_instance

    if _predict_pipeline_instance is None:
        _predict_pipeline_instance = PredictPipeline(config)

    return _predict_pipeline_instance