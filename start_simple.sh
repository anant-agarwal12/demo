#!/bin/bash
# Simple startup script for DoggoBot Face Detection

echo "======================================================================"
echo "🤖 DoggoBot - Simple Face Detection"
echo "======================================================================"
echo ""

# Check if in correct directory
if [ ! -d "scripts" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Run this from the DoggoBot root directory"
    exit 1
fi

echo "📦 Installing dependencies..."
cd scripts
pip install -q -r requirements.txt
cd ..

echo ""
echo "✅ Ready to start!"
echo ""
echo "Next steps:"
echo "  1. Terminal 1: cd backend && python main.py"
echo "  2. Terminal 2: cd frontend && npm run dev"
echo "  3. Terminal 3: cd scripts && python face_detector.py"
echo ""
echo "Or run face detector now? (y/N): "
read -r response

if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    echo ""
    echo "Mode: hog (CPU) or cnn (GPU)? [hog]: "
    read -r mode
    mode=${mode:-hog}
    
    echo ""
    echo "🚀 Starting face detector..."
    cd scripts
    python face_detector.py --mode "$mode"
else
    echo ""
    echo "👍 Run manually when ready:"
    echo "   cd scripts && python face_detector.py"
fi

echo ""
echo "======================================================================"
