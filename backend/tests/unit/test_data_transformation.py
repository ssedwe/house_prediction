import os
import shutil
import pytest
import pandas as pd
import joblib
import numpy as np
from backend.src.components.data_transformation import DataTransformation
from backend.src.entity.config_entity import DataTransformationConfig

# ==============================================================
# ARRANGE: THE SETUP FIXTURE
# ==============================================================
@pytest.fixture
def setup_transformation_environment():
    """Creates fake train/test data matching your schema to test the custom transformer."""
    artifact_dir = "tests/dummy_artifacts"
    os.makedirs(artifact_dir, exist_ok=True)
    
    train_path = os.path.join(artifact_dir, "dummy_train.csv")
    test_path = os.path.join(artifact_dir, "dummy_test.csv")
    preprocessor_path = os.path.join(artifact_dir, "preprocessor.pkl")
    
    # Fake data with the exact columns needed for FeatureEngineeringWrapper
    # Note: yr_built and yr_renovated are essential for your custom logic
    df = pd.DataFrame({
        "bedrooms": [3, 4], "bathrooms": [2, 3], "sqft_living": [1500, 2500],
        "sqft_lot": [5000, 6000], "floors": [1, 2], "waterfront": [0, 0],
        "view": [0, 1], "condition": [3, 4], "grade": [7, 8],
        "sqft_above": [1000, 2000], "sqft_basement": [500, 500], 
        "yr_built": [1990, 2005], "yr_renovated": [0, 2015],
        "zipcode": [98000, 98001], "lat": [47.0, 47.1],
        "long": [-122.0, -122.1], "sqft_living15": [1500, 2400],
        "price": [400000, 600000]
    })
    
    df.to_csv(train_path, index=False)
    df.to_csv(test_path, index=False)
    
    # FIXED: Included artifact_dir to prevent TypeError
    config = DataTransformationConfig(
        artifact_dir=artifact_dir,
        preprocessor_obj_file_path=preprocessor_path,
        train_data_path=train_path,
        test_data_path=test_path
    )
    
    yield config
    
    # TEARDOWN: Force delete the dummy directory and all files inside
    if os.path.exists(artifact_dir):
        shutil.rmtree(artifact_dir)

# ==============================================================
# ACT & ASSERT
# ==============================================================
def test_data_transformation_pipeline(setup_transformation_environment):
    config = setup_transformation_environment
    transformer = DataTransformation(config=config)
    
    # 1. ACT: Run the transformation
    transformer.initiate_data_transformation()
    
    # 2. ASSERT: Did the preprocessor.pkl file get saved?
    assert os.path.exists(config.preprocessor_obj_file_path), "Preprocessor was not saved to disk"
    
    # 3. ASSERT: Verification of Custom Logic
    # Load the saved pipeline and verify it can handle a single row of raw data
    saved_preprocessor = joblib.load(config.preprocessor_obj_file_path)
    
    raw_input = pd.DataFrame([{
        "bedrooms": 3, "bathrooms": 2, "sqft_living": 1500, "sqft_lot": 5000, 
        "floors": 1, "waterfront": 0, "view": 0, "condition": 3, "grade": 7,
        "sqft_above": 1000, "sqft_basement": 500, "yr_built": 2000, 
        "yr_renovated": 0, "zipcode": 98000, "lat": 47.0, "long": -122.0, 
        "sqft_living15": 1500
    }])
    
    # This checks if FeatureEngineeringWrapper + ColumnTransformer works as a unit
    transformed_data = saved_preprocessor.transform(raw_input)
    
    # The output of a StandardScaler/OneHotEncoder pipeline is a numpy array
    assert isinstance(transformed_data, np.ndarray), "Output should be a scaled numpy array"
    assert transformed_data.shape[0] == 1, "Output rows should match input rows"
    assert not np.isnan(transformed_data).any(), "Transformation resulted in NaNs"