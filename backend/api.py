from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import your ML pipeline from the src folder
from src.pipeline.predict_pipeline import PredictPipeline, CustomData

app = FastAPI(title="House Price Inference Engine")

# 1. Define the strict JSON structure the API accepts
class HouseFeatures(BaseModel):
    square_footage: float
    bedrooms: int
    bathrooms: int
    location_type: str
    # Add any other features your model was trained on here!

# 2. Health check for Docker Compose and Kubernetes
@app.get("/health")
def health_check():
    return {"status": "Inference Engine is Running and Secure"}

# 3. The Pure JSON Prediction Endpoint
@app.post("/predict")
def predict_price(features: HouseFeatures):
    try:
        # Map the incoming JSON to your CustomData class
        data = CustomData(
            square_footage=features.square_footage,
            bedrooms=features.bedrooms,
            bathrooms=features.bathrooms,
            location_type=features.location_type
        )
        
        # Convert to DataFrame
        pred_df = data.get_data_as_data_frame()
        
        # Run the heavy ML inference
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        
        # Return pure JSON
        return {"predicted_price": results[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))