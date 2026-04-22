from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import os
import logging
import mlflow

from dotenv import load_dotenv

# CRITICAL MLOPS IMPORT: We must import the custom wrapper so joblib can unpickle it!


# ---------------- ENV ----------------
load_dotenv()

DAGSHUB_USERNAME = os.getenv("DAGSHUB_USERNAME")
DAGSHUB_TOKEN = os.getenv("DAGSHUB_TOKEN")

if DAGSHUB_USERNAME and DAGSHUB_TOKEN:
    os.environ["MLFLOW_TRACKING_USERNAME"] = DAGSHUB_USERNAME
    os.environ["MLFLOW_TRACKING_PASSWORD"] = DAGSHUB_TOKEN

mlflow.set_tracking_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")
mlflow.set_registry_uri("https://dagshub.com/ssedwe/house_prediction.mlflow")

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- APP INIT ----------------
app = FastAPI(title="House Price Prediction API", version="1.0.0")

# ---------------- CORS ----------------
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:9090").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
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

# ---------------- MODEL ----------------
model = None
preprocessor = None

@app.on_event("startup")
def load_model():
    global model
    try:
        logger.info("Connecting to MLflow and loading Unified Pipeline...")
        # Note: We use @Production or /Production depending on your MLflow version
        model = mlflow.pyfunc.load_model("models:/HousePriceModel/Production")
        logger.info("Model loaded successfully from MLflow")
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        raise e

# ---------------- PREDICTION ENDPOINT ----------------
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_datapoint(data: HouseData):
    try:
        logger.info("Received prediction request")

        # Convert input data to DataFrame
        df = pd.DataFrame([data.model_dump()])
        logger.info("Input data converted to DataFrame")

        # The 'model' is now a Unified Pipeline. It handles transformation automatically!
        logger.info("Executing unified prediction pipeline...")
        prediction = model.predict(df)

        if hasattr(prediction, "__len__"):
            predicted_price = float(prediction[0])
        else:
            predicted_price = float(prediction)

        logger.info(f"Prediction success: ${predicted_price:,.2f}")
        return PredictionResponse(predicted_price=predicted_price)

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

# ---------------- HEALTH CHECK ----------------
@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

# ---------------- OPTIONS HANDLERS ----------------
@app.options("/api/v1/predict")
async def options_predict():
    return {}

@app.options("/api/v1/health")
async def options_health():
    return {}