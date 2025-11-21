#!/bin/bash
echo "🚀 Starting Kimi Chat History Combined Server (API + Dashboard)..."
cd server
python3 -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
