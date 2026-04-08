# 1. Use the official lightweight Python image (Debian-based, safe for ML libraries)
FROM python:3.9-slim

# 2. Set environment variables to optimize Python inside Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# 3. Create a non-root user for enterprise security
RUN addgroup --system appuser && adduser --system --group appuser

# 4. Set the working directory
WORKDIR /app

# 5. Copy ONLY requirements first to leverage Docker layer caching
COPY requirements.txt .

# 6. Upgrade pip and install dependencies without storing massive cache files
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of the application code
COPY . .

# 8. Transfer ownership of the files to the secure non-root user
RUN chown -R appuser:appuser /app

# 9. Switch away from the root user
USER appuser

# 10. Expose the port the app runs on
EXPOSE 8000

# 11. Start the FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]