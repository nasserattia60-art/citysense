#!/bin/bash
# CitySense Build Script for Render
# Runs during the build phase before starting the application

set -e

echo "=== CitySense Build Started ==="

# Install Python dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --no-input

echo "=== CitySense Build Completed Successfully ==="
