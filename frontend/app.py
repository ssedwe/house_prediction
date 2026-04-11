from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI(title="House Price Web UI")

# Initialize Jinja2 to render your HTML files
templates = Jinja2Templates(directory="templates")

# Read the internal backend URL from Docker Compose
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Renders the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict_datapoint(
    request: Request,
    # WARNING: Update these to match the exact 'name' attributes in your HTML form!
    square_footage: float = Form(...),
    bedrooms: int = Form(...),
    bathrooms: int = Form(...),
    location_type: str = Form(...)
):
    """Takes user form input, sends it to the Backend Engine, and returns the result."""
    
    # 1. Package the user's form data into JSON
    payload = {
        "square_footage": square_footage,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "location_type": location_type
    }

    try:
        # 2. Send a secure POST request over the internal Docker network to the ML Backend
        response = requests.post(f"{BACKEND_API_URL}/predict", json=payload)
        
        # 3. Check if the backend crashed
        response.raise_for_status() 
        
        # 4. Extract the prediction from the backend's JSON response
        prediction_result = response.json().get("predicted_price")
        
    except requests.exceptions.RequestException as e:
        prediction_result = f"Error connecting to ML Engine: {str(e)}"

    # 5. Render the HTML page again, passing the final result to display
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "results": prediction_result}
    )