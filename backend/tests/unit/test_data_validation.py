import os
import shutil
import pytest
import pandas as pd
import yaml
from backend.src.components.data_validation import DataValidation
from backend.src.entity.config_entity import DataValidationConfig

@pytest.fixture
def setup_validation_environment():
    artifact_dir = "tests/dummy_artifacts"
    os.makedirs(artifact_dir, exist_ok=True)

    raw_path = os.path.join(artifact_dir, "dummy_raw.csv")

    # 1. Create Dummy CSV Data
    df = pd.DataFrame({
        "bedrooms": [3, 4],
        "bathrooms": [2, 3],
        "price": [400000, 600000]
    })
    df.to_csv(raw_path, index=False)

    # 2. Create GOOD schema file
    good_schema_path = os.path.join(artifact_dir, "good_schema.yaml")
    good_content = {
        "columns": {
            "bedrooms": "int",
            "bathrooms": "int",
            "price": "int"
        }
    }
    with open(good_schema_path, "w") as f:
        yaml.dump(good_content, f)

    # 3. Create BAD schema file (expects a missing column)
    bad_schema_path = os.path.join(artifact_dir, "bad_schema.yaml")
    bad_content = {
        "columns": {
            "bedrooms": "int",
            "sqft_living": "int",  # This does not exist in our CSV
            "price": "int"
        }
    }
    with open(bad_schema_path, "w") as f:
        yaml.dump(bad_content, f)

    yield {
        "artifact_dir": artifact_dir,
        "raw_path": raw_path,
        "good_schema": good_schema_path,
        "bad_schema": bad_schema_path
    }

    # Teardown
    if os.path.exists(artifact_dir):
        shutil.rmtree(artifact_dir)


def test_data_validation_success(setup_validation_environment):
    env = setup_validation_environment
    
    # 1. Setup Config
    config = DataValidationConfig(
        raw_data_path=env["raw_path"],
        artifact_dir=env["artifact_dir"],
        schema_file_path=env["good_schema"]
    )

    # 2. LOAD the schema dictionary (This was the missing piece!)
    with open(env["good_schema"], "r") as f:
        schema_dict = yaml.safe_load(f)["columns"]

    # 3. Instantiate with BOTH required arguments
    validator = DataValidation(config=config, schema=schema_dict)

    # 4. Act & Assert
    result = validator.initiate_data_validation()
    assert result is True


def test_data_validation_failure(setup_validation_environment):
    env = setup_validation_environment
    
    # 1. Setup Config
    config = DataValidationConfig(
        raw_data_path=env["raw_path"],
        artifact_dir=env["artifact_dir"],
        schema_file_path=env["bad_schema"]
    )

    # 2. LOAD the bad schema dictionary
    with open(env["bad_schema"], "r") as f:
        schema_dict = yaml.safe_load(f)["columns"]

    # 3. Instantiate
    validator = DataValidation(config=config, schema=schema_dict)

    # 4. Act & Assert
    result = validator.initiate_data_validation()
    assert result is False