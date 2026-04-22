document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('submit-btn');
    const resultDiv = document.getElementById('result');
    const priceValue = document.getElementById('price-value');
    
    // REPLACE THIS URL with your actual Render Backend URL
    const API_URL = "https://house-predictio-backend.onrender.com/api/v1/predict";
    
    btn.innerText = "Calculating...";
    btn.disabled = true; // Prevent double-clicks while the model is thinking
    
    // Gather all 17 features from the UI
    const requestData = {
        bedrooms: parseInt(document.getElementById('bedrooms').value),
        bathrooms: parseFloat(document.getElementById('bathrooms').value),
        sqft_living: parseInt(document.getElementById('sqft_living').value),
        sqft_lot: parseInt(document.getElementById('sqft_lot').value),
        floors: parseFloat(document.getElementById('floors').value),
        waterfront: parseInt(document.getElementById('waterfront').value),
        view: parseInt(document.getElementById('view').value),
        condition: parseInt(document.getElementById('condition').value),
        grade: parseInt(document.getElementById('grade').value),
        sqft_above: parseInt(document.getElementById('sqft_above').value),
        sqft_basement: parseInt(document.getElementById('sqft_basement').value),
        yr_built: parseInt(document.getElementById('yr_built').value),
        yr_renovated: parseInt(document.getElementById('yr_renovated').value),
        zipcode: parseInt(document.getElementById('zipcode').value),
        lat: parseFloat(document.getElementById('lat').value),
        long: parseFloat(document.getElementById('long').value),
        sqft_living15: parseInt(document.getElementById('sqft_living15').value)
    };

    console.log("SENDING TO API:", requestData);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        
        if (response.ok) {
            // Your API returns { "predicted_price": float }
            const price = data.predicted_price; 
            
            // Format the number to a clean currency string
            priceValue.innerText = "$" + Number(price).toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            
            resultDiv.classList.remove('hidden');
            resultDiv.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Handle validation errors from FastAPI
            const errorMsg = data.detail ? JSON.stringify(data.detail) : "Unknown API Error";
            alert("Error from API: " + errorMsg);
        }
    } catch (error) {
        // This usually triggers if the Render free-tier backend is still "waking up"
        alert("Could not connect to the server. The backend might be starting up—please try again in 30 seconds.");
        console.error("Connection Error:", error);
    } finally {
        btn.innerText = "Predict Price";
        btn.disabled = false;
    }
});