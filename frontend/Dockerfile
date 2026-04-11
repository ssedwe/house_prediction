# /frontend/Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

RUN addgroup --system appuser && adduser --system --group appuser

WORKDIR /app

# Copy requirements (you need to create this file: frontend/requirements.txt)
# It should ONLY contain: fastapi, uvicorn, jinja2, python-multipart, requests
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

# The outside world will talk to the frontend on port 8080
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]