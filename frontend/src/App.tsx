import { lazy, Suspense } from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import LoadingSpinner from './components/LoadingSpinner'
import PageTransition from './components/PageTransition'

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

// Custom loading spinner with message
const PageLoading = () => (
  <LoadingSpinner size="lg" message="Loading" color="white" />
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-black">
          <Routes>
            <Route path="/" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <LaunchScreen />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/home" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <HomePage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/signup" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <SignupPage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/login" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <LoginPage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/dietary-preferences" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <DietaryPrefsPage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/recipe/:id" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <RecipeDetailsPage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/profile" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <ProfilePage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/favorites" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <FavoritesPage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/ingredient-recommendations" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <IngredientRecommendationPage />
                </PageTransition>
              </Suspense>
            } />
            <Route path="/recipes" element={
              <Suspense fallback={<PageLoading />}>
                <PageTransition>
                  <RecipesPage />
                </PageTransition>
              </Suspense>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App