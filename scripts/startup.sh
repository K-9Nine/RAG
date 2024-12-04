#!/bin/bash

# Load documents into Weaviate
echo "Loading documents into Weaviate..."
python src/utils/load_test_docs.py

# Start the FastAPI server
echo "Starting FastAPI server..."
uvicorn src.app:app --host 0.0.0.0 --port 8000 