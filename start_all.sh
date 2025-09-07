#!/bin/bash

echo "🌾 Starting AgriGuard Insurance Application..."
echo "=============================================="

# Function to start backend
start_backend() {
    echo "🚀 Starting FastAPI Backend..."
    cd projects/App-backend
    python start_server.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    cd ../..
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting React Frontend..."
    cd projects/App-frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ../..
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 3
start_frontend

echo ""
echo "✅ Services started successfully!"
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
