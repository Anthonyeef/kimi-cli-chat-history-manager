#!/bin/bash
echo "🚀 Starting Kimi Chat History with web server..."
cd server
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 --log-level error &
API_PID=$!
cd ..
sleep 2
cd dashboard
python3 -m http.server 8081 &
WEB_PID=$!
echo ""
echo "Dashboard: http://localhost:8081/index.html"
echo "API Docs:  http://127.0.0.1:8001/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
trap "kill $API_PID $WEB_PID; exit 0" INT
wait
