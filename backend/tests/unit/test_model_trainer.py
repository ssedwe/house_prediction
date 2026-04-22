import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.src.components.model_trainer import ModelTrainer
from backend.src.entity.config_entity import ModelTrainerConfig

# ==============================================================
# ARRANGE: THE SETUP FIXTURE
# ==============================================================
@pytest.fixture
def setup_trainer_environment():
    os.makedirs("tests/dummy_artifacts", exist_ok=True)
    train_path = "tests/dummy_artifacts/dummy_train.csv"
    test_path = "tests/dummy_artifacts/dummy_test.csv"
    
    # Fake raw data (the trainer drops the target and transforms the rest)
    df = pd.DataFrame({
        "feature1": [1.5, 2.5, 3.5, 4.5],
        "feature2": [10, 20, 30, 40],
        "price": [100, 200, 300, 400]
    })
    df.to_csv(train_path, index=False)
    df.to_csv(test_path, index=False)
    
    config = ModelTrainerConfig(
        train_data_path=train_path,
        test_data_path=test_path,
        artifact_dir="tests/dummy_artifacts",
        model_name="model.joblib",
        target_column="price"
    )
    
    yield config
    
    # TEARDOWN
    model_path = os.path.join(config.artifact_dir, config.model_name)
    for file in [train_path, test_path, model_path]:
        if os.path.exists(file):
            os.remove(file)
    if os.path.exists("tests/dummy_artifacts"):
        os.rmdir("tests/dummy_artifacts")

# ==============================================================
# ACT & ASSERT: THE MOCKED TEST
# ==============================================================
# We use @patch to intercept external calls during the test
@patch("backend.src.components.model_trainer.mlflow.tracking.MlflowClient")
@patch("backend.src.components.model_trainer.mlflow")
@patch("backend.src.components.model_trainer.read_yaml")
@patch("backend.src.components.model_trainer.joblib.load")
def test_model_trainer(mock_joblib_load, mock_read_yaml, mock_mlflow, mock_mlflow_client_class, setup_trainer_environment):
    config = setup_trainer_environment
    
    # 1. Mock the Preprocessor: Instead of loading the real one, return a dummy
    # that just passes the data through unchanged so the models can train.
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.side_effect = lambda x: x 
    mock_joblib_load.return_value = mock_preprocessor
    
    # 2. Mock the params.yaml: Provide simple parameters so GridSearch is fast
    mock_read_yaml.return_value = {
        "RandomForestRegressor": {"n_estimators": [10]},
        "DecisionTreeRegressor": {"max_depth": [2]},
        "GradientBoostingRegressor": {"n_estimators": [10]}
    }
    
    # 3. Mock MLflow Client for model promotion
    mock_client = MagicMock()
    mock_mlflow_client_class.return_value = mock_client
    
    # Mock get_latest_versions to return a fake version
    mock_version = MagicMock()
    mock_version.version = "1"
    mock_client.get_latest_versions.return_value = [mock_version]
    
    # 4. Instantiate and Act
    trainer = ModelTrainer(config=config)
    trainer.train()
    
    # ASSERT: Did the Champion Model save to the hard drive?
    model_path = os.path.join(config.artifact_dir, config.model_name)
    assert os.path.exists(model_path), "Champion model was not saved!"
    
    # Verify that MLflow was called correctly
    mock_mlflow.set_registry_uri.assert_called_once()
    mock_mlflow.sklearn.autolog.assert_called_once()
    
    # Verify that model promotion was attempted
    mock_client.get_latest_versions.assert_called_once_with("HousePriceModel")
    mock_client.transition_model_version_stage.assert_called_once()