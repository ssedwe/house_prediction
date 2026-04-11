#!/bin/bash

# 1. Setup DVC and Pull Models from Dagshub
# Hugging Face will inject these variables from its 'Secrets' settings
dvc remote modify origin --local auth basic
dvc remote modify origin --local user $DAGSHUB_USERNAME
dvc remote modify origin --local password $DAGSHUB_TOKEN
dvc pull -r origin

# 2. Start the ML Backend (In the background)
# We run it on port 8000 internally
cd /app/backend && uvicorn api:app --host 0.0.0.0 --port 8000 &

# 3. Start the Web Frontend (In the foreground)
# Hugging Face REQUIRES the public port to be 7860
cd /app/frontend && uvicorn app:app --host 0.0.0.0 --port 7860