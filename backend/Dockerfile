# 1. Base image
FROM python:3.11-slim

# 2. Set working directory to the top level
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first (cache optimization)
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire backend folder into a 'backend' directory inside the container
# This is the magic step that makes your 'backend.src...' imports work!
COPY . /app/backend

# 7. Expose port
EXPOSE 8000

# 8. Run production server
# We now tell Gunicorn to look inside backend -> src -> api.py
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.src.api:app", "--bind", "0.0.0.0:8000"]