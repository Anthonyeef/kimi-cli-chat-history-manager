#!/bin/bash

echo "Starting Kimi CLI Chat History API Server..."
echo "Server will run on http://127.0.0.1:8001"
echo "API documentation: http://127.0.0.1:8001/docs"
echo ""

cd server
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
