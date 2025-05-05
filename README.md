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
- React 18 with TypeScript
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

### Integrated Development Setup
The React frontend is built and served through the Django backend, allowing for a seamless development experience.

```bash
# Clone the repository
git clone https://github.com/yourusername/cuisine-craft.git
cd cuisine-craft

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Build the frontend (in development mode)
cd frontend
npm run build
cd ..

# Run migrations
cd backend
python manage.py migrate

# Start the Django server
python manage.py runserver
```

You can now access the application at http://localhost:8000

### Development Workflow
For active frontend development, you can either:

1. **Rebuild and refresh**: After making changes to React files:
   ```
   cd frontend
   npm run build
   ```
   Then refresh your browser.

2. **Stand-alone frontend** (for rapid development):
   ```
   cd frontend
   npm start
   ```
   This runs the React app standalone on http://localhost:3000, with API requests proxied to the Django server (which needs to be running). Note: Some backend-integrated features may require using the full integrated setup.

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
├── backend/                  # Django backend application
│   ├── cuisine_craft_project/# Django project core
│   ├── recipes/              # Recipe models and logic
│   ├── users/                # User authentication and profiles
│   ├── recommendations/      # Recipe recommendation system
│   ├── ingredients/          # Ingredient management
│   └── ...
├── requirements.txt          # Python dependencies
└── build.sh                  # Build script for deployment
```

## Usage

1. Register a new account or log in with existing credentials
2. Browse the recipe collection from the home page
3. Click on any recipe to view detailed information
4. Add recipes to favorites by clicking the heart icon
5. Follow cooking instructions by clicking "View Recipe Details"

## API Endpoints

The application uses RESTful API endpoints for data exchange:

- `/api/auth/` - Authentication endpoints
- `/api/recipes/` - Recipe listing and search
- `/api/recipes/:id/` - Detailed recipe information
- `/api/recipes/:id/favorite/` - Toggle recipe favorite status
- `/api/recipes/:id/cooked/` - Mark recipe as cooked
