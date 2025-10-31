#!/bin/bash

# DoggoBot Dashboard Startup Script
# This script helps you quickly start the entire stack

set -e

echo "?? DoggoBot Dashboard Startup"
echo "=============================="
echo ""

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "? Docker Compose found"
    echo ""
    echo "Starting services with Docker..."
    echo ""
    
    # Start services
    docker-compose up -d
    
    echo ""
    echo "? Services started!"
    echo ""
    echo "?? Access points:"
    echo "   - Dashboard:  http://localhost:3000"
    echo "   - Backend:    http://localhost:8000"
    echo "   - API Docs:   http://localhost:8000/docs"
    echo ""
    echo "?? View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "?? Stop services:"
    echo "   docker-compose down"
    echo ""
    
    # Optionally start detector
    read -p "Start detector example? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Starting detector (press Ctrl+C to stop)..."
        cd scripts
        pip install -q -r requirements.txt
        python detector_example.py
    fi
    
else
    echo "??  Docker Compose not found"
    echo ""
    echo "Would you like to start manually?"
    echo ""
    echo "Backend setup:"
    echo "  cd backend"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  python main.py"
    echo ""
    echo "Frontend setup (in another terminal):"
    echo "  cd frontend"
    echo "  npm install"
    echo "  npm run dev"
    echo ""
    echo "Detector (in another terminal):"
    echo "  cd scripts"
    echo "  pip install -r requirements.txt"
    echo "  python detector_example.py"
    echo ""
fi
