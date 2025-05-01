#!/usr/bin/env bash
# exit on error
set -o errexit

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

# Collect static files
python manage.py collectstatic --no-input 