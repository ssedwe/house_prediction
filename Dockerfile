# 1. Use the official lightweight Python image
FROM python:3.9-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# 3. Create a non-root user
RUN addgroup --system appuser && adduser --system --group appuser

# 4. Set the working directory
WORKDIR /app

# 5. Copy requirements first
COPY requirements.txt .

# 6. Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of the application code
COPY . .

# 8. Transfer ownership to the secure user
RUN chown -R appuser:appuser /app

# 9. Switch to the secure user
USER appuser

# 10. Expose the port
EXPOSE 7860

# 11. Configure DAGsHub, Pull the Model, and Start the Server
CMD ["sh", "-c", "dvc remote add origin https://dagshub.com/shashi2160/house_prediction.dvc -f && dvc remote modify origin --local auth basic && dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc pull -r origin && uvicorn app:app --host 0.0.0.0 --port 7860"]