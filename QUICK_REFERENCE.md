# QUICK REFERENCE: ModelTrainer Dependencies

## 🎯 All Dependent Files at a Glance

### Direct Imports (3 files)
```
✅ backend/src/pipeline/stage_04_model_trainer.py
   └─ Imports: from backend.src.components.model_trainer import ModelTrainer
   └─ Uses: ModelTrainer(config=model_trainer_config).train()
   
✅ backend/tests/unit/test_model_trainer.py
   └─ Imports: from backend.src.components.model_trainer import ModelTrainer
   └─ Uses: For unit testing train() method
   
✅ backend/main.py (INDIRECT)
   └─ Imports: from backend.src.pipeline.stage_04_model_trainer import ModelTrainerTrainingPipeline
   └─ Uses: Part of orchestrated pipeline
```

### Configuration Dependencies (3 files)
```
✅ backend/src/entity/config_entity.py
   └─ Defines: ModelTrainerConfig dataclass (5 fields)
   
✅ backend/src/config/configuration.py
   └─ Method: get_model_trainer_config() -> ModelTrainerConfig
   
✅ config/config.yaml
   └─ Section: model_trainer with paths and model name
```

### MLflow Dependencies (2 concepts)
```
✅ MLflow Experiment: "House_Price_Prediction"
   └─ Set in: model_trainer.py line 62
   └─ Used for: Tracking training runs
   
✅ MLflow Model Registration: "HousePriceModel"
   └─ Registered in: model_trainer.py line 97
   └─ Consumed by: predict_pipeline.py and api.py
```

### Downstream Consumers (4 files)
```
✅ backend/src/components/model_evaluation.py
   └─ Loads: artifacts/model_trainer/model.joblib
   └─ Purpose: Evaluate model on test set
   
✅ backend/src/pipeline/stage_05_model_evaluation.py
   └─ Depends on: stage_04_model_trainer.py output
   └─ Purpose: Orchestrate evaluation stage
   
✅ backend/src/pipeline/predict_pipeline.py
   └─ Loads: MLflow model "HousePriceModel@production"
   └─ Purpose: Production prediction service
   
✅ backend/src/api.py
   └─ Loads: MLflow model "HousePriceModel@production" 
   └─ Purpose: FastAPI prediction endpoint
```

### Parameter Dependencies (2 files)
```
✅ params.yaml
   └─ Used for: GridSearchCV hyperparameter tuning
   └─ Keys: RandomForestRegressor, DecisionTreeRegressor, GradientBoostingRegressor
   
✅ dvc.yaml
   └─ Used for: Pipeline orchestration and artifact tracking
   └─ Dependencies: model_trainer.py, preprocessor.pkl, train.csv
```

### Test Files (2 files)
```
✅ backend/tests/unit/test_model_trainer.py
   └─ Tests: ModelTrainer.train() method
   └─ Mocks: mlflow, joblib.load, read_yaml
   
✅ backend/tests/integration/test_api.py
   └─ Tests: End-to-end prediction via API
   └─ Requires: MLflow model at @production stage
```

---

## 📊 Dependency Impact by Change Type

| Change Type | Impact Radius | Files Affected | Severity |
|-------------|---------------|----------------|----------|
| Add/Remove Algorithm | Algorithm layer | params.yaml, test | Low |
| Change Model Name | Config + Downstream | config.yaml, predict_pipeline, api | Medium |
| Change Registration Name | MLflow + Downstream | model_trainer, predict_pipeline, api | High |
| Change Data Paths | Config layer | config.yaml, config_entity | Low |
| Change ModelTrainerConfig | Config + Component | config_entity, configuration, model_trainer | High |
| Change train() Signature | Component + Pipeline | stage_04, tests | High |
| Change Experiment Name | MLflow only | model_trainer (1 line) | Low |

---

## 🔄 Execution Order (Pipeline Stages)

```
Stage 1: Data Ingestion
    ↓
Stage 2: Data Validation
    ↓
Stage 3: Data Transformation → Creates preprocessor.pkl
    ↓
Stage 4: MODEL TRAINING ← ModelTrainer runs here
    ↓ (depends on)
    ├─ artifacts/data_transformation/preprocessor.pkl
    ├─ artifacts/data_ingestion/train.csv
    ├─ artifacts/data_ingestion/test.csv
    ├─ params.yaml (hyperparameters)
    └─ config.yaml (paths)
    
    ↓ (produces)
    ├─ artifacts/model_trainer/model.joblib
    ├─ MLflow runs (House_Price_Prediction experiment)
    └─ MLflow model registry (HousePriceModel)
    ↓
Stage 5: Model Evaluation
    ↓ (uses)
    └─ artifacts/model_trainer/model.joblib
    
    ↓ (produces)
    └─ artifacts/model_evaluation/metrics.json
```

---

## 🚀 Where ModelTrainer Output is Used

### 1. Model Evaluation (stage_05_model_trainer.py)
```python
model = joblib.load(self.config.model_path)  # Loads model.joblib
predicted_qualities = model.predict(test_x_transformed)  # Uses model
```

### 2. Prediction Service (predict_pipeline.py)
```python
model = mlflow.pyfunc.load_model("models:/HousePriceModel@production")
preds = self.model.predict(data_scaled)  # Uses MLflow registered model
```

### 3. API Service (api.py)
```python
model = mlflow.pyfunc.load_model("models:/HousePriceModel@production")
prediction = model.predict(df)  # Uses MLflow registered model
```

---

## ⚡ Quick Change Checklist

### If modifying ModelTrainer logic:
- [ ] Update model_trainer.py
- [ ] Update test_model_trainer.py mocks if internal calls change
- [ ] Test that model.joblib is still saved correctly
- [ ] Run full pipeline to verify

### If changing output path/name:
- [ ] Update config.yaml: model_trainer.model_name
- [ ] Update config.yaml: model_trainer.artifact_dir (if needed)
- [ ] Update dvc.yaml: model_trainer.outs path
- [ ] Update model_evaluation.py config if path changed
- [ ] Run full pipeline to verify

### If changing registered model name:
- [ ] Update model_trainer.py: registered_model_name parameter (line 97)
- [ ] Update predict_pipeline.py: load_model path (line 43)
- [ ] Update api.py: load_model path (line 72)
- [ ] Update MLflow to promote model to @production stage
- [ ] Test API endpoint after promotion

### If changing experiment name:
- [ ] Update model_trainer.py: mlflow.set_experiment() (line 62)
- [ ] No other code changes needed
- [ ] Old experiment data remains in MLflow

### If adding ModelTrainerConfig fields:
- [ ] Update config_entity.py: Add field to dataclass
- [ ] Update configuration.py: Map field in get_model_trainer_config()
- [ ] Update config.yaml: Add corresponding YAML section
- [ ] Update model_trainer.py: Use new field in __init__ or train()
- [ ] Update test_model_trainer.py: Add field to fixture

---

## 📍 Critical File Locations

**Core Component:**
- `backend/src/components/model_trainer.py` ⭐

**Configuration:**
- `backend/src/entity/config_entity.py` (ModelTrainerConfig)
- `backend/src/config/configuration.py` (get_model_trainer_config)
- `config/config.yaml` (model_trainer section)
- `params.yaml` (algorithm parameters)

**Pipeline Integration:**
- `backend/src/pipeline/stage_04_model_trainer.py` (Wrapper)
- `backend/main.py` (Entry point)

**MLflow:**
- Experiment: "House_Price_Prediction"
- Model: "HousePriceModel" (stages: None → production)

**Output Artifacts:**
- `artifacts/model_trainer/model.joblib` (joblib format)
- `artifacts/model_evaluation/metrics.json` (metrics only)

**Downstream:**
- `backend/src/components/model_evaluation.py` (Consumes joblib)
- `backend/src/pipeline/predict_pipeline.py` (Consumes MLflow)
- `backend/src/api.py` (Consumes MLflow)

**Tests:**
- `backend/tests/unit/test_model_trainer.py` (Unit tests)
- `backend/tests/integration/test_api.py` (E2E tests)

---

## 🎯 Key Dependencies Summary

**What ModelTrainer IMPORTS:**
- scikit-learn (RandomForest, DecisionTree, GradientBoosting)
- MLflow (logging, registry)
- joblib (model serialization)
- pandas (data handling)
- Custom: data_transformation (FeatureEngineeringWrapper), config_entity, logger

**What ModelTrainer READS:**
- artifacts/data_ingestion/train.csv
- artifacts/data_ingestion/test.csv
- artifacts/data_transformation/preprocessor.pkl
- params.yaml (hyperparameters)

**What ModelTrainer WRITES:**
- artifacts/model_trainer/model.joblib (saved model)
- MLflow tracking runs
- MLflow model registry

**What Depends on ModelTrainer:**
- Stage 5: Model Evaluation (reads model.joblib)
- Prediction Pipeline (reads HousePriceModel from MLflow)
- API Service (reads HousePriceModel from MLflow)
- Unit Tests (tests train() method)
- Integration Tests (tests full pipeline)

---

## 🔗 Reference Links

- **Full Analysis:** See DEPENDENCY_ANALYSIS.md
- **Model Trainer:** backend/src/components/model_trainer.py
- **Configuration:** config/config.yaml (lines 29-33)
- **Parameters:** params.yaml (full file)
- **DVC Pipeline:** dvc.yaml (lines 35-47)
- **MLflow Tracking:** https://dagshub.com/ssedwe/house_prediction.mlflow

---

**Last Updated:** 2024
**Status:** Complete
**Total Dependencies Analyzed:** 14 files + 2 config files + MLflow service
