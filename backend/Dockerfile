# 1. Start with a lightweight Python 3.9 operating system
FROM python:3.9-slim-buster

# 2. Create a folder inside the container called /app
WORKDIR /app

# 3. Copy your requirements list into the container
COPY requirements.txt .

# 4. Install all the Python libraries
# (We use --no-cache-dir to keep the container size small)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your project code into the container
COPY . .

# 6. Open port 8000 so the outside world can talk to FastAPI
EXPOSE 8000

# 7. The command to turn the server on when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]