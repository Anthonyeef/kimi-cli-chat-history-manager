#!/bin/bash

# 🚀 Kimi Chat History - Combined Start Script
# Starts both API server and SvelteKit frontend in parallel

echo "🚀 Starting Kimi Chat History Application..."
echo "=============================================="
echo ""

# Kill any existing processes on these ports
echo "🧹 Cleaning up existing processes..."
lsof -ti :8001 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti :5173 2>/dev/null | xargs kill -9 2>/dev/null
sleep 2

# Check if we're in the right directory
if [ ! -d "server" ] || [ ! -d "web" ]; then
    echo "❌ Error: Please run this script from the kimi-chat-history root directory"
    exit 1
fi

# Check if npm dependencies are installed
if [ ! -d "web/node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    cd web
    npm install
    cd ..
fi

# Start API server
echo "🔧 Starting API server on http://localhost:8001..."
cd server
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload --log-level info &
API_PID=$!
cd ..

# Wait for API to be ready
echo "⏳ Waiting for API server to start..."
sleep 3

# Start SvelteKit frontend
echo "🎨 Starting SvelteKit frontend on http://localhost:5173..."
echo "Note: First run may show tsconfig warnings - this is normal!"
cd web
npm run dev &
WEB_PID=$!
cd ..

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to initialize (15 seconds for first run)..."
sleep 15

# Check if frontend started properly
if ! ps -p $WEB_PID > /dev/null; then
    echo "❌ Frontend failed to start. Check errors above."
    echo "💡 Tip: Try running 'cd web && npm run dev' manually to see detailed errors"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Clear screen and show status
clear
echo ""
echo "✅ Kimi Chat History is ready!"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📖 API Docs: http://localhost:8001/docs"
echo "🔍 API Root: http://localhost:8001/api"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $API_PID 2>/dev/null
    kill $WEB_PID 2>/dev/null
    wait $API_PID 2>/dev/null
    wait $WEB_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set up trap for Ctrl+C
trap cleanup INT

# Keep script running
wait
