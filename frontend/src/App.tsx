import React, { lazy, Suspense, useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import LoadingSpinner from './components/LoadingSpinner'

// Lazy load pages
const LaunchScreen = lazy(() => import('./pages/LaunchScreen'))
const HomePage = lazy(() => import('./pages/HomePage'))
const SignupPage = lazy(() => import('./pages/SignupPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const DietaryPrefsPage = lazy(() => import('./pages/DietaryPrefsPage'))
const RecipeDetailsPage = lazy(() => import('./pages/RecipeDetailsPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const FavoritesPage = lazy(() => import('./pages/FavoritesPage'))
const IngredientRecommendationPage = lazy(() => import('./pages/IngredientRecommendationPage'))
const RecipesPage = lazy(() => import('./pages/RecipesPage'))

// Improved loading spinner that only shows for genuinely slow loads
const PageLoading = () => {
  const [show, setShow] = useState(false);
  
  useEffect(() => {
    // Only show spinner for loads taking longer than 1500ms
    const timer = setTimeout(() => {
      setShow(true);
    }, 1500);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Return empty div for fast loads, spinner only for slow loads
  return show ? (
    <div className="min-h-screen bg-red-400 flex flex-col items-center justify-center">
      <div className="loading loading-bars loading-lg text-white"></div>
      <div className="mt-4 text-white font-medium">Loading</div>
    </div>
  ) : <div className="min-h-screen bg-red-400"></div>; // Empty div maintains background color
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-red-400">
          <Suspense fallback={<PageLoading />}>
            <Routes>
              <Route path="/" element={<LaunchScreen />} />
              <Route path="/home" element={<HomePage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/dietary-preferences" element={<DietaryPrefsPage />} />
              <Route path="/recipe/:id" element={<RecipeDetailsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/favorites" element={<FavoritesPage />} />
              <Route path="/ingredient-recommendations" element={<IngredientRecommendationPage />} />
              <Route path="/recipes" element={<RecipesPage />} />
            </Routes>
          </Suspense>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App