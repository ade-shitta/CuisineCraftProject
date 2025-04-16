

import { useState, useEffect, useCallback, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import { recipes as recipesApi } from "../services/api"
import LoadingSpinner from "../components/LoadingSpinner"
import { ApiRecipe } from "../types/api"

interface RecipeResult {
  id: string;
  title: string;
  image?: string;
  isFavorite: boolean;
}

const IngredientRecommendationPage = () => {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const modalRef = useRef<HTMLDivElement>(null)
  
  // State variables
  const [ingredientsInput, setIngredientsInput] = useState("")
  const [recipeResults, setRecipeResults] = useState<RecipeResult[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login")
    }
  }, [isAuthenticated, navigate, isLoading])

  // Handle click outside modal to close it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        setShowModal(false)
      }
    }

    if (showModal) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showModal])

  // Handle ingredient search submission
  const handleSearchSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!ingredientsInput.trim()) return
    
    setLoading(true)
    
    try {
      const response = await recipesApi.searchByIngredients(ingredientsInput.trim())
      
      const recipes = response.data.map((recipe: ApiRecipe) => ({
        id: recipe.recipe_id,
        title: recipe.title,
        image: recipe.image_url,
        isFavorite: recipe.isFavorite
      }))
      
      setRecipeResults(recipes)
      setShowModal(true)
    } catch (error) {
      console.error("Error searching recipes by ingredients:", error)
    } finally {
      setLoading(false)
    }
  }, [ingredientsInput])

  // Handle recipe selection
  const handleRecipeClick = useCallback((recipeId: string) => {
    navigate(`/recipe/${recipeId}`)
  }, [navigate])

  // Render the modal with recipe results
  const renderRecipeModal = () => {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 p-4">
        <div ref={modalRef} className="bg-white rounded-3xl w-full max-w-xl px-6 py-8 shadow-xl">
          <h2 className="text-xl font-medium text-center mb-8 text-gray-500">Possible Recipes With Your Current Ingredients</h2>
          
          {recipeResults.length === 0 ? (
            <p className="text-center py-6 text-gray-400">No recipes found with these ingredients.</p>
          ) : (
            <div className="space-y-4 max-h-[450px] overflow-y-auto px-4">
              {recipeResults.map(recipe => (
                <div 
                  key={recipe.id}
                  onClick={() => handleRecipeClick(recipe.id)}
                  className="bg-red-500 text-white rounded-2xl py-4 px-5 flex justify-between items-center cursor-pointer hover:bg-red-600 transition-colors shadow-md"
                >
                  <span className="text-base font-medium">{recipe.title}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              ))}
            </div>
          )}
          
          <div className="mt-8 flex justify-center">
            <button
              onClick={() => setShowModal(false)}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-8 py-2 rounded-full transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="min-h-screen bg-red-400 flex flex-col">
      <div className="absolute top-4 right-4">
        <Header />
      </div>
      
      <div className="flex-grow flex flex-col items-center justify-center p-4">
        <div className="bg-white rounded-3xl w-full max-w-xl p-6 shadow-lg">
          <h2 className="text-xl font-medium text-center mb-6 text-gray-500">Possible Recipes With Your Current Ingredients</h2>
          
          <form onSubmit={handleSearchSubmit} className="space-y-4">
            <div className="bg-red-200 bg-opacity-50 rounded-full p-4">
              <input
                type="text"
                value={ingredientsInput}
                onChange={(e) => setIngredientsInput(e.target.value)}
                placeholder="Add Your Ingredients Here"
                className="w-full bg-transparent text-center text-red-600 placeholder-red-400 focus:outline-none text-lg"
              />
            </div>
            
            <div className="flex justify-center mt-4">
              <button
                type="submit"
                disabled={loading}
                className="bg-red-500 text-white hover:bg-red-600 px-6 py-2 rounded-full shadow-md transition-colors focus:outline-none focus:ring-2 focus:ring-red-400 disabled:opacity-50 w-auto max-w-xs mx-auto"
              >
                {loading ? 'Searching...' : 'Search Recipes'}
              </button>
            </div>
          </form>
          
          <div className="mt-4 text-gray-500 text-center text-sm">
            Enter ingredients separated by commas (e.g., "chicken, rice, garlic")
          </div>
        </div>
      </div>
      
      {showModal && renderRecipeModal()}
    </div>
  )
}

export default IngredientRecommendationPage