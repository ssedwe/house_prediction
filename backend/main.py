import sys
from backend.src.logger import logger
from backend.src.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
from backend.src.pipeline.stage_02_data_validation import DataValidationTrainingPipeline
from backend.src.pipeline.stage_03_data_transformation import DataTransformationTrainingPipeline
from backend.src.pipeline.stage_04_model_trainer import ModelTrainerTrainingPipeline
from backend.src.pipeline.stage_05_model_evaluation import ModelEvaluationTrainingPipeline

def run_pipeline():
    try:
        logger.info(">>>>>>>>>> ENTERPRISE TRAINING PIPELINE INITIATED <<<<<<<<<<")
        
        # Stage 1: Ingestion (MongoDB)
        logger.info(">>> Stage 1: Data Ingestion Started")
        DataIngestionTrainingPipeline().main()
        
        # Stage 2: Validation
        logger.info(">>> Stage 2: Data Validation Started")
        DataValidationTrainingPipeline().main()
        
        # Stage 3: Transformation (Custom Scikit-Learn Wrapper)
        logger.info(">>> Stage 3: Data Transformation Started")
        DataTransformationTrainingPipeline().main()
        
        # Stage 4: Training (GridSearch)
        logger.info(">>> Stage 4: Model Training Started")
        ModelTrainerTrainingPipeline().main()
        
        # Stage 5: Evaluation (MLflow & DagsHub)
        logger.info(">>> Stage 5: Model Evaluation Started")
        ModelEvaluationTrainingPipeline().main()
        
        logger.info(">>>>>>>>>> TRAINING PIPELINE COMPLETED SUCCESSFULLY <<<<<<<<<<")
        
    except Exception as e:
        logger.exception(f"Pipeline failed at runtime: {e}")
        sys.exit(1) # Tells Docker the container crashed

if __name__ == '__main__':
    run_pipeline()