FROM python:3.9-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all code (frontend, backend, artifacts, .dvc)
COPY . .

# Install dependencies for both microservices
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Grant permission to the startup script
RUN chmod +x /app/start.sh

# HF Spaces usually runs as user 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Open the HF port
EXPOSE 7860

CMD ["/app/start.sh"]