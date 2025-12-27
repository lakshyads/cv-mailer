#!/bin/bash

# Frontend Setup Script for CV Mailer Dashboard

set -e  # Exit on error

echo "🎨 Setting up CV Mailer Web Dashboard..."
echo ""

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
echo "✓ Node.js version: $(node --version)"

if [ "$node_version" -lt 18 ]; then
    echo "⚠️  Warning: Node.js 18+ is recommended for best compatibility."
    echo "   Your version: $(node --version)"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✓ npm version: $(npm --version)"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    echo "   Try running: npm cache clean --force && npm install"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# API URL (optional, defaults to /api/v1 which uses Vite proxy)
# VITE_API_URL=http://localhost:8000/api/v1
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Quick Start:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Make sure the API is running:"
echo "   cd .. && source venv/bin/activate && cv-mailer-api"
echo ""
echo "2. Start the development server:"
echo "   npm run dev"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  npm run dev       # Start development server"
echo "  npm run build     # Build for production"
echo "  npm run preview   # Preview production build"
echo "  npm run lint      # Run linter"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 For more information, see:"
echo "   - README.md (in this directory)"
echo "   - ../docs/WEB_DASHBOARD_GUIDE.md"
echo ""

