import pytest
import httpx
import numpy as np

# Change this to your local or docker container URL
BASE_URL = "http://localhost:8000" 

@pytest.fixture
def valid_house_data():
    """Returns a valid payload matching the house_prediction schema."""
    return {
        "bedrooms": 3, "bathrooms": 2.25, "sqft_living": 2570, "sqft_lot": 7242,
        "floors": 2.0, "waterfront": 0, "view": 0, "condition": 3, "grade": 7,
        "sqft_above": 2170, "sqft_basement": 400, "yr_built": 1951, 
        "yr_renovated": 1991, "zipcode": 98125, "lat": 47.721, "long": -122.319,
        "sqft_living15": 1690
    }

@pytest.mark.asyncio
async def test_predict_endpoint_success(valid_house_data):
    """
    Test Case 1: Happy Path
    Verifies that a valid payload returns a 200 OK and a numeric prediction.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/v1/predict", json=valid_house_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Industry check: Ensure the key 'predicted_price' exists and is a positive number
        assert "predicted_price" in data
        assert isinstance(data["predicted_price"], (int, float))
        assert data["predicted_price"] > 0

@pytest.mark.asyncio
async def test_predict_endpoint_invalid_data():
    """
    Test Case 2: Validation Error (422/400)
    Verifies that missing or wrong data types are caught by the API.
    """
    bad_data = {"bedrooms": "three", "price": "expensive"} # Wrong types
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/v1/predict", json=bad_data)
        
        # FastAPI returns 422 for Unprocessable Entity
        assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_api_latency():
    """
    Test Case 3: Performance SLA Check
    Verifies the model responds within a specific time limit (e.g., 500ms).
    """
    payload = {k: 1.0 for k in ["bedrooms", "bathrooms", "sqft_living", "sqft_lot", 
                                "floors", "waterfront", "view", "condition", "grade",
                                "sqft_above", "sqft_basement", "yr_built", 
                                "yr_renovated", "zipcode", "lat", "long", "sqft_living15"]}
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/v1/predict", json=payload)
        
        # Ensure response time is under 500ms for industrial responsiveness
        assert response.elapsed.total_seconds() < 0.5

@pytest.mark.asyncio
async def test_health_check():
    """
    Test Case 4: Liveness Probe
    Standard check used by Kubernetes to see if the container is alive.
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"