#!/usr/bin/env bash
# exit on error
set -o errexit

# Create media directory on persistent disk if it doesn't exist
mkdir -p /opt/render/project/src/backend/media
echo "Created media directory"

# Build frontend
cd frontend
npm install
# Set CI=false to prevent treating warnings as errors
CI=false npm run build
cd ..

# Build backend
cd backend
python -m pip install --upgrade pip
pip install -r ../requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Import recipes data from TheMealDB API
python import_data.py

# Collect static files
python manage.py collectstatic --no-input 