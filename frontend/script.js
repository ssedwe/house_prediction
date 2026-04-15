document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('submit-btn');
    const resultDiv = document.getElementById('result');
    const priceValue = document.getElementById('price-value');
    
    btn.innerText = "Calculating...";
    
    // Dynamically gather ALL 17 features from the UI, matching houses.csv schema perfectly
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
        const response = await fetch('http://localhost:8000/api/v1/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        
        if (response.ok) {
            // Adjust "predicted_price" to whatever key your API actually returns
            const price = data.predicted_price || data; 
            priceValue.innerText = "$" + Number(price).toLocaleString(undefined, {minimumFractionDigits: 2});
            resultDiv.classList.remove('hidden');
        } else {
            alert("Error from API: " + JSON.stringify(data));
        }
    } catch (error) {
        alert("Failed to connect to the backend API.");
        console.error(error);
    } finally {
        btn.innerText = "Predict Price";
    }
});