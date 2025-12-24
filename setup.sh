#!/bin/bash

echo "🚀 Setting up Food Inventory Backend"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "✅ Created .env file - please update with your settings"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "
from app.database import engine
from app.models import raw_material, food_item, order
raw_material.Base.metadata.create_all(bind=engine)
food_item.Base.metadata.create_all(bind=engine)
order.Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Add sample data
echo "🌱 Adding sample data..."
python seed_data.py

echo ""
echo "🎉 Backend setup completed!"
echo ""
echo "📋 To start the server:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "🌐 API will be available at:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/health"