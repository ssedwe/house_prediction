from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import os
import logging

# Import pipeline
from backend.src.pipeline.predict_pipeline import PredictPipeline

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- APP INIT ----------------
app = FastAPI(title="House Price Prediction API", version="1.0.0")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9090"],  # change to frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------- SCHEMA ----------------
class HouseData(BaseModel):
    bedrooms: int = Field(gt=0, le=20)
    bathrooms: float = Field(gt=0, le=10)
    sqft_living: int = Field(gt=100)
    sqft_lot: int = Field(gt=100)
    floors: float = Field(gt=0, le=5)
    waterfront: int = Field(ge=0, le=1)
    view: int = Field(ge=0, le=4)
    condition: int = Field(ge=1, le=5)
    grade: int = Field(ge=1, le=13)
    sqft_above: int = Field(gt=0)
    sqft_basement: int = Field(ge=0)
    yr_built: int = Field(ge=1800, le=2025)
    yr_renovated: int = Field(ge=0, le=2025)
    zipcode: int
    lat: float
    long: float
    sqft_living15: int = Field(gt=0)


class PredictionResponse(BaseModel):
    predicted_price: float


# ---------------- CONFIG ----------------
class PredictionConfig:
    preprocessor_path = os.getenv("PREPROCESSOR_PATH", "artifacts/data_transformation/preprocessor.pkl")
    model_path = os.getenv("MODEL_PATH", "artifacts/model_trainer/model.joblib")


# ---------------- LOAD MODEL ON STARTUP ----------------
predict_pipeline = None

@app.on_event("startup")
def load_model():
    global predict_pipeline
    try:
        logger.info("Loading model and preprocessor...")
        config = PredictionConfig()
        predict_pipeline = PredictPipeline(config)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        raise e


# ---------------- CORS OPTIONS HANDLER ----------------
@app.options("/api/v1/predict")
async def options_predict():
    return {}


# ---------------- PREDICTION ENDPOINT ----------------
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_datapoint(data: HouseData):
    try:
        logger.info("Received prediction request")

        df = pd.DataFrame([data.dict()])

        results = predict_pipeline.predict(df)

        prediction = float(results[0])

        logger.info(f"Prediction success: {prediction}")

        return PredictionResponse(predicted_price=prediction)

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


# ---------------- HEALTH CHECK ----------------
@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}


# Also add OPTIONS for health endpoint
@app.options("/api/v1/health")
async def options_health():
    return {}
