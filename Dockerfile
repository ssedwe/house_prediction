# 1. Use the official lightweight Python image
FROM python:3.9-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# 3. Install Git (Crucial for DVC)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 4. Create a non-root user
RUN addgroup --system appuser && adduser --system --group appuser

# 5. Set the working directory
WORKDIR /app

# 6. Copy requirements first
COPY requirements.txt .

# 7. Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 8. Copy the rest of the application code (This copies your .dvc folder)
COPY . .

# 9. Create a dummy Git repo so DVC doesn't crash
RUN git init && \
    git config user.email "mlops@enterprise.com" && \
    git config user.name "MLOps Bot" && \
    git add . && \
    git commit -m "Dummy commit to satisfy DVC"

# 10. Transfer ownership to the secure user
RUN chown -R appuser:appuser /app

# 11. Switch to the secure user
USER appuser

# 12. Expose the port
EXPOSE 7860

# 13. Authenticate with DAGsHub, Pull Model, and Start Server
CMD ["sh", "-c", "dvc remote modify origin --local auth basic && dvc remote modify origin --local user $DAGSHUB_USERNAME && dvc remote modify origin --local password $DAGSHUB_TOKEN && dvc pull -r origin && uvicorn app:app --host 0.0.0.0 --port 7860"]