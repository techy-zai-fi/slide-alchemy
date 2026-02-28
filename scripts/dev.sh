#!/bin/bash
set -e

echo "Starting SlideAlchemy dev environment..."

# Start backend
cd backend
pip install -r requirements.txt -q
python -m uvicorn app.main:app --port 8741 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend
echo "Waiting for backend..."
for i in {1..10}; do
    if curl -s http://localhost:8741/health > /dev/null 2>&1; then
        echo "Backend ready!"
        break
    fi
    sleep 1
done

# Start frontend + Tauri
npm run tauri dev

# Cleanup
kill $BACKEND_PID 2>/dev/null
echo "Dev environment stopped."
