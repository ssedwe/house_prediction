from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Import your prediction pipeline
from src.pipeline.predict_pipeline import CustomData, PredictPipeline
from src.logger import logger

# ==============================================================
# 1. LIFESPAN EVENT (Solves the Disk Read Bottleneck)
# ==============================================================
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Enterprise Server...")
    logger.info("Loading preprocessor and Champion model into RAM. Please wait.")
    
    # Load the pipeline ONCE and store it in memory
    ml_models["prediction_engine"] = PredictPipeline()
    logger.info("Model successfully cached in memory. Ready for high traffic!")
    
    yield # Server runs and handles traffic here
    
    logger.info("Server shutting down. Clearing RAM.")
    ml_models.clear()


# Initialize the FastAPI App with the lifespan manager
app = FastAPI(
    title="Enterprise House Price Predictor API",
    description="A production-ready ML API for predicting house prices.",
    version="1.0.0",
    lifespan=lifespan
)

# Tell FastAPI where to find the HTML files
templates = Jinja2Templates(directory="templates")


# ==============================================================
# 2. PYDANTIC SCHEMA (The Ironclad Data Contract)
# ==============================================================
class HouseDataInput(BaseModel):
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

    class Config:
        json_schema_extra = {
            "example": {
                "bedrooms": 3.0, "bathrooms": 2.0, "sqft_living": 1500,
                "sqft_lot": 5000, "floors": 1.0, "waterfront": 0, "view": 0,
                "condition": 3, "grade": 7, "sqft_above": 1500, "sqft_basement": 0,
                "yr_built": 1990, "yr_renovated": 0, "zipcode": 98178,
                "lat": 47.5112, "long": -122.257, "sqft_living15": 1500
            }
        }


# ==============================================================
# 3. ROUTES AND ENDPOINTS
# ==============================================================

@app.get("/health")
async def health_check():
    """Cloud infrastructure pings this to ensure the server is alive."""
    return {"status": "healthy", "model_loaded": "prediction_engine" in ml_models}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Renders the frontend HTML page."""
    # FIXED: Added strict keyword arguments for the template response
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/predict", response_class=HTMLResponse)
async def predict_html(
    request: Request,
    bedrooms: float = Form(...), bathrooms: float = Form(...), sqft_living: int = Form(...),
    sqft_lot: int = Form(...), floors: float = Form(...), waterfront: int = Form(...),
    view: int = Form(...), condition: int = Form(...), grade: int = Form(...),
    sqft_above: int = Form(...), sqft_basement: int = Form(...), yr_built: int = Form(...),
    yr_renovated: int = Form(...), zipcode: int = Form(...), lat: float = Form(...),
    long: float = Form(...), sqft_living15: int = Form(...)
):
    """Handles form submissions directly from the HTML page."""
    try:
        data = CustomData(
            bedrooms=bedrooms, bathrooms=bathrooms, sqft_living=sqft_living, sqft_lot=sqft_lot,
            floors=floors, waterfront=waterfront, view=view, condition=condition, grade=grade,
            sqft_above=sqft_above, sqft_basement=sqft_basement, yr_built=yr_built,
            yr_renovated=yr_renovated, zipcode=zipcode, lat=lat, long=long, sqft_living15=sqft_living15
        )
        
        pred_df = data.get_data_as_data_frame()
        
        # Predict using the RAM-cached engine!
        results = ml_models["prediction_engine"].predict(pred_df) 
        final_price = round(results[0], 2)
        
        # FIXED: Added strict keyword arguments for context and template name
        return templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context={"results": f"${final_price:,}"}
        )
    except Exception as e:
        return HTMLResponse(content=f"An error occurred: {e}", status_code=500)


@app.post("/api/v1/predict")
async def predict_json(input_data: HouseDataInput):
    """The REST API endpoint for mobile apps, React frontends, and other services."""
    try:
        data = CustomData(**input_data.dict())
        pred_df = data.get_data_as_data_frame()
        
        # Predict using the RAM-cached engine!
        results = ml_models["prediction_engine"].predict(pred_df)
        
        return JSONResponse(content={
            "predicted_price": round(results[0], 2),
            "currency": "USD",
            "status": "success"
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)