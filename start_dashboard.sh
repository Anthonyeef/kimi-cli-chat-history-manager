#!/bin/bash

echo "🚀 Starting Kimi CLI Chat History Dashboard..."
echo ""
echo "1. Starting API server..."
cd server
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 --log-level error &
SERVER_PID=$!
echo "   ✓ Server started (PID: $SERVER_PID)"
echo "   API Docs: http://127.0.0.1:8001/docs"
echo ""
echo "2. Opening dashboard in browser..."
sleep 2  # Wait for server to be ready

# Try to open with different commands based on OS
if command -v open >/dev/null 2>&1; then
    # macOS
    open ../dashboard/index.html
    echo "   ✓ Dashboard opened with 'open'"
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open ../dashboard/index.html
    echo "   ✓ Dashboard opened with 'xdg-open'"
elif command -v start >/dev/null 2>&1; then
    # Windows (Git Bash)
    start ../dashboard/index.html
    echo "   ✓ Dashboard opened with 'start'"
else
    echo "   ⚠ Could not open browser automatically"
    echo "   Please manually open: dashboard/index.html"
fi

echo ""
echo "3. Dashboard URLs:"
echo "   - Dashboard: file:///Users/yifen/Workspace/kimi-chat-history/dashboard/index.html"
echo "   - API:       http://127.0.0.1:8001"
echo ""
echo "4. Features to test:"
echo "   ✓ Search conversations by name or content"
echo "   ✓ Filter by workspace"
echo "   ✓ View chat details with tool calls and think blocks"
echo "   ✓ New: Activity heatmap showing conversation patterns"
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""

# Keep script running until Ctrl+C
trap "echo ''; echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT
wait $SERVER_PID