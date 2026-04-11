# /backend/Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install Git for DVC
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appuser && adduser --system --group appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Dummy git commit to satisfy DVC's strict requirements
RUN git init && \
    git config user.email "mlops@enterprise.com" && \
    git config user.name "MLOps Engine" && \
    git add . && \
    git commit -m "Initialize DVC environment"

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# INDUSTRY UPGRADE: Using --workers 4 for concurrent prediction handling
CMD ["sh", "-c", "dvc remote modify origin --local auth basic && dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc pull -r origin && uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4"]