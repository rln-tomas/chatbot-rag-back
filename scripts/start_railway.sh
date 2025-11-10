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

# Run migrations with verbose output and error handling
if alembic upgrade head -v; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migration failed with exit code $?"
    echo "Printing full traceback..."
    exit 1
fi

echo ""
echo "=================================================="
echo "Step 2: Starting Uvicorn Server"
echo "=================================================="

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
