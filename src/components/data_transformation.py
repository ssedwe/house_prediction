import os
import sys
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin  # <-- NEW: Allows Custom Transformers
import joblib
from src.logger import logger
from src.exception import CustomException
from src.entity.config_entity import DataTransformationConfig

# ==========================================================
# 1. THE CUSTOM TRANSFORMER (Baking Pandas into Scikit-Learn)
# ==========================================================
class FeatureEngineeringWrapper(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self  # Nothing to mathematically fit for age calculation
        
    def transform(self, X):
        # Create a copy so we don't alter the original dataframe accidentally
        X_copy = X.copy()
        
        # Apply our logical math
        X_copy['house_age'] = 2024 - X_copy['yr_built']
        X_copy['is_renovated'] = X_copy['yr_renovated'].apply(lambda x: 1 if x > 0 else 0)
        
        # Drop the redundant columns
        X_copy = X_copy.drop(columns=['yr_built', 'yr_renovated', 'sqft_above'])
        return X_copy

# ==========================================================
# 2. THE MAIN CLASS
# ==========================================================
class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def get_data_transformer_object(self):
        try:
            # Note: These are the columns that will exist AFTER the FeatureEngineeringWrapper runs
            numeric_features = ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 
                                'floors', 'condition', 'grade', 'sqft_basement', 
                                'lat', 'long', 'sqft_living15', 'house_age']
            
            categorical_features = ['zipcode', 'waterfront', 'view', 'is_renovated']

            num_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])

            cat_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("one_hot", OneHotEncoder(handle_unknown="ignore"))
            ])

            # The Column Transformer does the splitting
            column_transformer = ColumnTransformer(
                transformers=[
                    ("num", num_pipeline, numeric_features),
                    ("cat", cat_pipeline, categorical_features)
                ]
            )

            # --- THE MASTER PIPELINE ---
            # 1st step: Apply Pandas logic. 2nd step: Split, scale, and encode!
            preprocessor = Pipeline(steps=[
                ("feature_engineering", FeatureEngineeringWrapper()),
                ("data_scaling", column_transformer)
            ])

            return preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self):
        try:
            logger.info("Loading train and test data")
            train_df = pd.read_csv(self.config.train_data_path)
            test_df = pd.read_csv(self.config.test_data_path)

            logger.info("Dropping missing values (NaNs) to protect Linear Regression")
            train_df.dropna(inplace=True)
            test_df.dropna(inplace=True)

            target_column_name = "price"

            # Split Independent (X) and Dependent (y)
            # NOTICE: We do NOT call feature engineering manually anymore!
            input_feature_train_df = train_df.drop(columns=[target_column_name])
            target_feature_train_df = train_df[target_column_name]

            logger.info("Obtaining advanced preprocessor object")
            preprocessor = self.get_data_transformer_object()

            logger.info("Fitting the preprocessor on the training data")
            # This automatically runs FeatureEngineeringWrapper -> ColumnTransformer
            preprocessor.fit(input_feature_train_df)

            logger.info(f"Saving preprocessor object to {self.config.preprocessor_obj_file_path}")
            joblib.dump(preprocessor, self.config.preprocessor_obj_file_path)
            logger.info("Data Transformation completed successfully.")

        except Exception as e:
            raise CustomException(e, sys)