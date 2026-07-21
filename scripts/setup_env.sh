#!/bin/bash
# Setup script for new development machines

echo "🚀 AML Monitoring System - Environment Setup"
echo "============================================"

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
else
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created - please edit with your local settings"
    echo ""
    echo "📝 Edit .env and set:"
    echo "   - DATABASE_PASSWORD (your local PostgreSQL password)"
    echo "   - SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    exit 1
fi

# Check Python version
echo ""
echo "🐍 Checking Python version..."
python --version

# Check uv is installed
echo ""
echo "📦 Checking uv package manager..."
uv --version

# Sync dependencies
echo ""
echo "📥 Installing dependencies..."
uv sync

# Check PostgreSQL connection
echo ""
echo "🗄️  Testing PostgreSQL connection..."
uv run python -c "import os; import psycopg2; from dotenv import load_dotenv; load_dotenv(); 
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print('✅ PostgreSQL connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')"

# Run migrations
echo ""
echo "🔄 Running Django migrations..."
uv run python manage.py migrate

# Collect static files
echo ""
echo "📦 Collecting static files..."
uv run python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development server:"
echo "   uv run python manage.py runserver"