from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from src.pipeline.predict_pipeline import PredictPipeline, CustomData

app = FastAPI(title="House Price Inference Engine")

class HouseFeatures(BaseModel):
    bedrooms: float
    bathrooms: float
    sqft_living: int
    sqft_lot: int
    floors: float
    waterfront: int
    view: int
    condition: int
    grade: int
    sqft_above: int
    sqft_basement: int
    yr_built: int
    yr_renovated: int
    zipcode: int
    lat: float
    long: float
    sqft_living15: int

@app.get("/health")
def health_check():
    return {"status": "Inference Engine is Running securely."}

@app.post("/predict")
def predict_price(features: HouseFeatures):
    try:
        data = CustomData(**features.dict())
        pred_df = data.get_data_as_data_frame()
        
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        
        return {"predicted_price": float(results[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))