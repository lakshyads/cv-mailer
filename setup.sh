#!/bin/bash

# CV Mailer Setup Script
# Updated for refactored package structure

set -e  # Exit on error

echo "🚀 Setting up CV Mailer..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check Python version and warn if outdated
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)
if [ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]; then
    echo "⚠️  Warning: Python 3.9 and below are past end-of-life."
    echo "   Consider upgrading to Python 3.10+ for better support."
    echo "   (The app will still work, but you may see deprecation warnings)"
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install the package in editable mode with API dependencies
echo "📥 Installing CV Mailer package (including API & development dependencies)..."
pip install -e ".[api,dev]" --quiet

echo "✓ Package installed (with API & development dependencies)"

# Create necessary directories
echo "📁 Creating data and logs directories..."
mkdir -p data logs assets
touch data/.gitkeep logs/.gitkeep assets/.gitkeep
echo "✓ Directories created"

# Check for credentials file
if [ ! -f "credentials.json" ]; then
    echo ""
    echo "⚠️  Warning: credentials.json not found!"
    echo "   Please download OAuth 2.0 credentials from Google Cloud Console:"
    echo "   1. Go to https://console.cloud.google.com/"
    echo "   2. Navigate to 'APIs & Services' > 'Credentials'"
    echo "   3. Create 'OAuth client ID' > Choose 'Desktop app'"
    echo "   4. Download JSON and save as 'credentials.json' in project root"
    echo ""
fi

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "✓ .env file created"
        echo "   ⚠️  Please edit .env with your configuration"
    else
        echo "⚠️  No .env.example found. Please create .env manually."
        echo "   See README.md for required environment variables."
    fi
else
    echo "✓ .env file already exists"
fi

# Initialize database (will be created on first run)
echo "🗄️  Database will be initialized on first run"

# Check if package is properly installed
if command -v cv-mailer &> /dev/null; then
    echo "✓ cv-mailer command is available"
else
    echo "⚠️  cv-mailer command not found in PATH"
    echo "   You may need to restart your terminal or run:"
    echo "   source venv/bin/activate"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 📝 Edit .env with your configuration:"
echo "   - SPREADSHEET_ID (from Google Sheets URL)"
echo "   - GMAIL_USER (your Gmail address)"
echo "   - SENDER_NAME (your full name)"
echo "   - RESUME_FILE_PATH or RESUME_DRIVE_LINK"
echo ""
echo "2. 🔑 Place credentials.json in project root"
echo "   (Download from Google Cloud Console)"
echo ""
echo "3. 📋 Set up your Google Sheet with required columns:"
echo "   - Company Name (required)"
echo "   - Position (required)"
echo "   - Recruiter Name/Names (required)"
echo "   - Location, Job Posting URL, Status (optional)"
echo ""
echo "4. 🚀 Test the setup:"
echo "   source venv/bin/activate  # Activate virtual environment"
echo "   cv-mailer --dry-run       # Test without sending emails"
echo ""
echo "5. 📖 For detailed instructions, see:"
echo "   - README.md (overview and quick start)"
echo "   - docs/SETUP_GUIDE.md (detailed setup)"
echo "   - docs/QUICK_START.md (beginner guide)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  cv-mailer            # Process new applications"
echo "  cv-mailer --dry-run  # Test without sending"
echo "  cv-mailer --stats    # Show statistics"
echo "  cv-mailer --help     # Show all options"
echo ""
echo "  cv-mailer-api        # Start REST API server (optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
