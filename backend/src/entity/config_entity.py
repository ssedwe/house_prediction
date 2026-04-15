from dataclasses import dataclass
from pathlib import Path


# ==============================
# Data Ingestion Config
# ==============================
@dataclass
class DataIngestionConfig:
    database_name: str
    collection_name: str
    artifact_dir: Path
    raw_data_path: Path
    train_data_path: Path   
    test_data_path: Path    
    test_size: float


# ==============================
# (Optional Future) Data Validation Config
# ==============================
@dataclass
class DataValidationConfig:
    artifact_dir: Path
    raw_data_path: Path
    schema_file_path: Path


# ==============================
# Data Transformation Config
# ==============================
@dataclass
class DataTransformationConfig:
    artifact_dir: Path
    train_data_path: Path
    test_data_path: Path
    preprocessor_obj_file_path: Path

# ==============================
# Model Trainer Config
# ==============================
@dataclass
class ModelTrainerConfig:
    artifact_dir: Path
    train_data_path: Path
    test_data_path: Path
    model_name: str
    target_column: str

# ==============================
# Model Evaluation Config
# ==============================

@dataclass
class ModelEvaluationConfig:
    root_dir: Path
    test_data_path: Path
    model_path: Path
    preprocessor_path: Path
    metric_file_name: Path
    target_column: str



@dataclass(frozen=True)
class PredictionConfig:
    model_path: Path
    preprocessor_path: Path