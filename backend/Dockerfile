# backend/Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 1. Start in the absolute root folder
WORKDIR /app

# 2. Copy the ENTIRE project into the container
COPY . .

# 3. Install the bulletproof requirements
RUN pip install --no-cache-dir -r backend/requirements.txt

# 4. Initialize dummy DVC so DAGsHub doesn't crash
RUN git init && \
    git config user.email "mlops@enterprise.com" && \
    git config user.name "MLOps Engine" && \
    git add . && \
    git commit -m "Initialize DVC environment"

EXPOSE 8000

# 5. THE SILVER BULLET: Move inside the backend folder BEFORE turning Uvicorn on
WORKDIR /app/backend

# 6. Boot sequence
CMD ["sh", "-c", "dvc remote modify origin --local auth basic && dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc pull -r origin && uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4"]