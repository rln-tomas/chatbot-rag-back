#!/bin/bash
set -e  # Exit on error

echo "=================================================="
echo "Starting Railway Deployment"
echo "=================================================="
echo "Environment: ${ENVIRONMENT:-production}"
echo "Port: ${PORT:-8000}"
echo ""

echo "=================================================="
echo "Step 1: Running Alembic Migrations"
echo "=================================================="

# Run migrations with error handling
if alembic upgrade head; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migration failed with exit code $?"
    exit 1
fi

echo ""
echo "=================================================="
echo "Step 2: Running Database Seeders"
echo "=================================================="

# Run seeders (creates test users if they don't exist)
if python scripts/seed.py; then
    echo "✅ Seeders completed successfully"
else
    echo "⚠️  Seeder failed, but continuing startup..."
    echo "   This is usually OK if data already exists"
fi

echo ""
echo "=================================================="
echo "Step 3: Starting Uvicorn Server"
echo "=================================================="

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
