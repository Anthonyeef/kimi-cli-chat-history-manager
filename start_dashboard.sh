#!/bin/bash

echo "🚀 Starting Kimi Chat History Dashboard..."
echo ""

# Kill any processes on these ports first
echo "Cleaning up existing processes..."
lsof -ti :8001 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti :8080 2>/dev/null | xargs kill -9 2>/dev/null
sleep 2

# Start API server
echo "1. Starting API server on port 8001..."
cd server
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 --log-level error &
API_PID=$!

cd ..
sleep 3

# Start web server
echo "2. Starting web server on port 8080..."
cd dashboard
python3 -m http.server 8080 &
WEB_PID=$!

cd ..
sleep 2

echo ""
echo "✅ Dashboard is ready!"
echo ""
echo "📍 Open: http://localhost:8080/index.html"
echo "📖 API:   http://127.0.0.1:8001/docs"
echo ""
echo "Try:"
echo "  1. Click any chat → URL changes"
echo "  2. Browser back → Returns to list"
echo "  3. Use #chat/{id} to deep-link"
echo ""
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $API_PID $WEB_PID 2>/dev/null; exit" INT
wait
