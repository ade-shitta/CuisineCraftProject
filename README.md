# CuisineCraft

CuisineCraft is a modern, full-stack recipe application designed to help food enthusiasts discover, save, and follow cooking instructions for their favorite dishes.

## Features

- **User Authentication**: Secure login and registration system
- **Recipe Discovery**: Browse and search through a variety of recipes
- **Recipe Details**: View comprehensive recipe information including:
  - High-quality images
  - Ingredient lists with measurements
  - Step-by-step cooking instructions
  - Dietary tags
- **Interactive Cooking**: Follow recipe steps with interactive checkboxes
- **Recipe Tracking**: Mark recipes as cooked to track your culinary journey
- **Favorites System**: Save your favorite recipes for quick access
- **Responsive Design**: Optimized for both desktop and mobile devices

## Tech Stack

### Frontend
- React 19 with TypeScript
- React Router for navigation
- Context API for state management
- Tailwind CSS for styling

### Backend
- Django 5.1
- Django REST Framework
- PostgreSQL database

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- npm or yarn
- pip

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Backend Setup
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Project Structure

```
CuisineCraftProject/
├── frontend/                 # React frontend application
│   ├── public/               # Public assets
│   └── src/
│       ├── components/       # Reusable UI components
│       ├── context/          # React context providers
│       ├── pages/            # Page components
│       ├── services/         # API service connectors
│       └── ...
└── backend/                  # Django backend application
    ├── api/                  # REST API endpoints
    ├── recipes/              # Recipe models and logic
    ├── users/                # User authentication and profiles
    └── ...
```

## Usage

1. Register a new account or log in with existing credentials
2. Browse the recipe collection from the home page
3. Click on any recipe to view detailed information
4. Add recipes to favorites by clicking the heart icon
5. Follow cooking instructions by clicking "View Recipe Details"
6. Track completed recipes through your profile

## API Endpoints

The application uses RESTful API endpoints for data exchange:

- `/api/auth/` - Authentication endpoints
- `/api/recipes/` - Recipe listing and search
- `/api/recipes/:id/` - Detailed recipe information
- `/api/recipes/:id/favorite/` - Toggle recipe favorite status
- `/api/recipes/:id/cooked/` - Mark recipe as cooked
