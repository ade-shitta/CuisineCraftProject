

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import { recipes } from "../services/api"
import { ApiRecipe } from "../types/api"

const FavoritesPage = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const [favorites, setFavorites] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Only redirect if we're done loading and not authenticated
    if (!isLoading && !isAuthenticated) {
      navigate("/login")
      return
    }
  }, [isAuthenticated, navigate, isLoading])

  useEffect(() => {
    if (!isAuthenticated) {
      return
    }

    const fetchFavorites = async () => {
      try {
        const favoritesResponse = await recipes.getFavorites()
        setFavorites(favoritesResponse.data.map((recipe: ApiRecipe) => ({
          id: recipe.recipe_id,
          title: recipe.title,
          image: recipe.image_url,
          isFavorite: true
        })))
        setLoading(false)
      } catch (error) {
        console.error("Error fetching favorites:", error)
        setLoading(false)
      }
    }

    fetchFavorites()
  }, [isAuthenticated])

  const handleToggleFavorite = async (id: string) => {
    try {
      await recipes.toggleFavorite(id)
      
      // Remove the recipe from favorites immediately for better UX
      setFavorites(favorites.filter(recipe => recipe.id !== id))
    } catch (error) {
      console.error("Error removing from favorites:", error)
    }
  }

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-red-400 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg text-white"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1"></div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Favorites</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      {favorites.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mx-auto max-w-6xl mb-8">
          {favorites.map((recipe) => (
            <div key={recipe.id} className="flex-shrink-0 transform transition duration-300 hover:scale-105">
              <div className="relative w-full aspect-square rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                <img 
                  src={recipe.image} 
                  alt={recipe.title} 
                  className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
                  onClick={() => navigate(`/recipe/${recipe.id}`)}
                />
                <button 
                  className="absolute top-2 right-2 bg-pink-100 rounded-full p-1.5 shadow-sm hover:bg-pink-200 transition-colors"
                  onClick={() => handleToggleFavorite(recipe.id)}
                  aria-label="Remove from favorites"
                  title="Remove from favorites"
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className="h-5 w-5 text-red-500" 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                  >
                    <path 
                      fillRule="evenodd" 
                      d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
                      clipRule="evenodd" 
                    />
                  </svg>
                </button>
                <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-xl py-2">
                  <p className="text-center text-gray-800 font-medium text-sm">{recipe.title}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-10">
          <p className="text-white text-lg mb-4">You haven't added any favorites yet</p>
          <button 
            onClick={() => navigate('/recipes')}
            className="btn bg-white text-red-500 hover:bg-red-100 border-none hover:scale-105 transition-transform duration-300 hover:shadow-md"
          >
            Explore Recipes
          </button>
        </div>
      )}
    </div>
  )
}

export default FavoritesPage