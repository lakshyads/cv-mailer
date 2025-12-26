#!/bin/bash

# CV Mailer Setup Script

echo "🚀 Setting up CV Mailer..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for credentials file
if [ ! -f "credentials.json" ]; then
    echo "⚠️  Warning: credentials.json not found!"
    echo "   Please download OAuth credentials from Google Cloud Console"
    echo "   and save as credentials.json in the project root"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "   Please edit .env with your configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from models import init_database; init_database()"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Place credentials.json in the project root"
echo "3. Run: source venv/bin/activate && python main.py --dry-run"

