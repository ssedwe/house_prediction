from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI(title="House Price Web UI")
templates = Jinja2Templates(directory="templates")

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict_datapoint(
    request: Request,
    bedrooms: float = Form(...), bathrooms: float = Form(...),
    sqft_living: int = Form(...), sqft_lot: int = Form(...),
    floors: float = Form(...), waterfront: int = Form(...),
    view: int = Form(...), condition: int = Form(...),
    grade: int = Form(...), sqft_above: int = Form(...),
    sqft_basement: int = Form(...), yr_built: int = Form(...),
    yr_renovated: int = Form(...), zipcode: int = Form(...),
    lat: float = Form(...), long: float = Form(...),
    sqft_living15: int = Form(...)
):
    payload = {
        "bedrooms": bedrooms, "bathrooms": bathrooms, "sqft_living": sqft_living,
        "sqft_lot": sqft_lot, "floors": floors, "waterfront": waterfront,
        "view": view, "condition": condition, "grade": grade,
        "sqft_above": sqft_above, "sqft_basement": sqft_basement, "yr_built": yr_built,
        "yr_renovated": yr_renovated, "zipcode": zipcode, "lat": lat,
        "long": long, "sqft_living15": sqft_living15
    }

    try:
        response = requests.post(f"{BACKEND_API_URL}/predict", json=payload)
        response.raise_for_status() 
        raw_price = response.json().get("predicted_price")
        prediction_result = f"${raw_price:,.2f}"
    except requests.exceptions.RequestException as e:
        prediction_result = f"Error: ML Backend is offline or processing failed."

    return templates.TemplateResponse("index.html", {"request": request, "results": prediction_result})