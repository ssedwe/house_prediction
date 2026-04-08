import sys
import pandas as pd
import joblib
from pathlib import Path
from src.exception import CustomException
from src.logger import logger

# CRITICAL IMPORT: So joblib knows how to unpickle your custom logic!
from src.components.data_transformation import FeatureEngineeringWrapper

class PredictPipeline:
    def __init__(self):
        try:
            # ==============================================================
            # THE BULLETPROOF PATH FIX
            # ==============================================================
            # 1. Find EXACTLY where this specific file (predict_pipeline.py) lives
            current_dir = Path(__file__).resolve().parent
            
            # 2. Walk backwards up the folder tree to the main project root
            # (From src/pipeline -> up to src -> up to root)
            project_root = current_dir.parent.parent
            
            # 3. Build the absolute path to the artifacts
            model_path = project_root / "artifacts" / "model_trainer" / "model.joblib"
            preprocessor_path = project_root / "artifacts" / "data_transformation" / "preprocessor.pkl"
            
            logger.info("Loading preprocessor and model from absolute paths...")
            self.model = joblib.load(model_path)
            self.preprocessor = joblib.load(preprocessor_path)
            logger.info("Artifacts loaded successfully!")
            
        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, features):
        try:
            # 1. Transform the raw data using our smart preprocessor
            data_scaled = self.preprocessor.transform(features)
            
            # 2. Make the prediction using our Champion Model
            preds = self.model.predict(data_scaled)
            return preds
            
        except Exception as e:
            raise CustomException(e, sys)


class CustomData:
    """
    Maps inputs from the HTML form / Pydantic JSON into a Pandas DataFrame.
    """
    def __init__(self, bedrooms: float, bathrooms: float, sqft_living: int, sqft_lot: int,
                 floors: float, waterfront: int, view: int, condition: int, grade: int,
                 sqft_above: int, sqft_basement: int, yr_built: int, yr_renovated: int,
                 zipcode: int, lat: float, long: float, sqft_living15: int):
        
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.sqft_living = sqft_living
        self.sqft_lot = sqft_lot
        self.floors = floors
        self.waterfront = waterfront
        self.view = view
        self.condition = condition
        self.grade = grade
        self.sqft_above = sqft_above
        self.sqft_basement = sqft_basement
        self.yr_built = yr_built
        self.yr_renovated = yr_renovated
        self.zipcode = zipcode
        self.lat = lat
        self.long = long
        self.sqft_living15 = sqft_living15

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "bedrooms": [self.bedrooms],
                "bathrooms": [self.bathrooms],
                "sqft_living": [self.sqft_living],
                "sqft_lot": [self.sqft_lot],
                "floors": [self.floors],
                "waterfront": [self.waterfront],
                "view": [self.view],
                "condition": [self.condition],
                "grade": [self.grade],
                "sqft_above": [self.sqft_above],
                "sqft_basement": [self.sqft_basement],
                "yr_built": [self.yr_built],
                "yr_renovated": [self.yr_renovated],
                "zipcode": [self.zipcode],
                "lat": [self.lat],
                "long": [self.long],
                "sqft_living15": [self.sqft_living15],
            }

            return pd.DataFrame(custom_data_input_dict)
            
        except Exception as e:
            raise CustomException(e, sys)