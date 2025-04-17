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

interface Substitution {
  ingredient: string;
  substitutes: string[];
}

interface AlmostMatchingRecipe {
  recipe: ApiRecipe;
  missing_ingredients: string[];
  substitutions: Substitution[];
  missing_count: number;
}

const IngredientRecommendationPage = () => {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const modalRef = useRef<HTMLDivElement>(null)
  
  // State variables
  const [ingredientsInput, setIngredientsInput] = useState("")
  const [recipeResults, setRecipeResults] = useState<RecipeResult[]>([])
  const [almostMatchingRecipes, setAlmostMatchingRecipes] = useState<AlmostMatchingRecipe[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'exact' | 'almost'>('exact')
  const [expandedSubstitutions, setExpandedSubstitutions] = useState<Record<string, boolean>>({})

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

  // Toggle substitution expansion
  const toggleSubstitution = (recipeId: string) => {
    setExpandedSubstitutions(prev => ({
      ...prev,
      [recipeId]: !prev[recipeId]
    }))
  }

  // Handle ingredient search submission
  const handleSearchSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!ingredientsInput.trim()) return
    
    setLoading(true)
    
    try {
      // Fetch exact matching recipes
      const exactMatchResponse = await recipesApi.searchByIngredients(ingredientsInput.trim())
      
      const recipes = exactMatchResponse.data.map((recipe: ApiRecipe) => ({
        id: recipe.recipe_id,
        title: recipe.title,
        image: recipe.image_url,
        isFavorite: recipe.isFavorite
      }))
      
      setRecipeResults(recipes)
      
      // Fetch almost matching recipes with substitution suggestions
      const almostMatchResponse = await recipesApi.getAlmostMatchingRecipes(
        ingredientsInput.trim(),
        2, // Max 2 missing ingredients
        10 // Limit to 10 results
      )
      
      setAlmostMatchingRecipes(almostMatchResponse.data)
      
      // Show results
      setShowModal(true)
      
      // Default to showing exact matches if available, otherwise show almost-matching
      setActiveTab(recipes.length > 0 ? 'exact' : 'almost')
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
        <div ref={modalRef} className="bg-white rounded-3xl w-full max-w-2xl px-6 py-8 shadow-xl">
          <h2 className="text-xl font-medium text-center mb-6 text-gray-700">Possible Recipes With Your Ingredients</h2>
          
          {/* Tabs */}
          <div className="flex border-b border-gray-200 mb-6">
            <button
              className={`flex-1 py-2 px-4 text-center ${activeTab === 'exact' ? 'border-b-2 border-red-500 text-red-500 font-medium' : 'text-gray-500'}`}
              onClick={() => setActiveTab('exact')}
            >
              Exact Matches {recipeResults.length > 0 && `(${recipeResults.length})`}
            </button>
            <button
              className={`flex-1 py-2 px-4 text-center ${activeTab === 'almost' ? 'border-b-2 border-red-500 text-red-500 font-medium' : 'text-gray-500'}`}
              onClick={() => setActiveTab('almost')}
            >
              Almost Matches {almostMatchingRecipes.length > 0 && `(${almostMatchingRecipes.length})`}
            </button>
          </div>
          
          {/* Exact Matches Tab */}
          {activeTab === 'exact' && (
            <div className="space-y-4 max-h-[400px] overflow-y-auto px-2">
              {recipeResults.length === 0 ? (
                <p className="text-center py-6 text-gray-400">No exact matches found. Check "Almost Matches" tab for recipes you can make with just a few more ingredients.</p>
              ) : (
                recipeResults.map(recipe => (
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
                ))
              )}
            </div>
          )}
          
          {/* Almost Matching Tab */}
          {activeTab === 'almost' && (
            <div className="space-y-6 max-h-[400px] overflow-y-auto px-2">
              {almostMatchingRecipes.length === 0 ? (
                <p className="text-center py-6 text-gray-400">No almost-matching recipes found with your ingredients.</p>
              ) : (
                almostMatchingRecipes.map(item => (
                  <div key={item.recipe.recipe_id} className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100">
                    <div 
                      onClick={() => handleRecipeClick(item.recipe.recipe_id)}
                      className="bg-red-500 text-white py-3 px-4 flex justify-between items-center cursor-pointer hover:bg-red-600 transition-colors"
                    >
                      <span className="text-base font-medium">{item.recipe.title}</span>
                      <div className="flex items-center">
                        <span className="bg-white text-red-500 text-xs font-bold rounded-full px-2 py-1 mr-2">
                          Missing {item.missing_count}
                        </span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                    
                    {/* Missing ingredients section */}
                    <div className="p-4">
                      <h3 className="text-sm font-semibold text-gray-500 mb-2">Missing Ingredients:</h3>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {item.missing_ingredients.map(ingredient => (
                          <span key={ingredient} className="bg-red-100 text-red-600 text-xs font-medium px-2 py-1 rounded-full">
                            {ingredient}
                          </span>
                        ))}
                      </div>
                      
                      {/* Substitution suggestions */}
                      {item.substitutions.length > 0 && (
                        <div className="mt-3">
                          <button
                            onClick={() => toggleSubstitution(item.recipe.recipe_id)}
                            className="text-sm text-blue-500 flex items-center"
                          >
                            <span>{expandedSubstitutions[item.recipe.recipe_id] ? 'Hide' : 'Show'} substitution ideas</span>
                            <svg 
                              xmlns="http://www.w3.org/2000/svg" 
                              className={`h-4 w-4 ml-1 transform transition-transform ${expandedSubstitutions[item.recipe.recipe_id] ? 'rotate-180' : ''}`} 
                              viewBox="0 0 20 20" 
                              fill="currentColor"
                            >
                              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                          </button>
                          
                          {expandedSubstitutions[item.recipe.recipe_id] && (
                            <div className="mt-2 pl-2 border-l-2 border-blue-200">
                              {item.substitutions.map(sub => (
                                <div key={sub.ingredient} className="mb-2">
                                  <span className="text-xs font-medium text-gray-600">
                                    Instead of <span className="text-red-500">{sub.ingredient}</span>, try:
                                  </span>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {sub.substitutes.length > 0 ? (
                                      sub.substitutes.map(substitute => (
                                        <span key={substitute} className="bg-green-100 text-green-600 text-xs px-2 py-0.5 rounded">
                                          {substitute}
                                        </span>
                                      ))
                                    ) : (
                                      <span className="text-xs text-gray-500">No substitutions found</span>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
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
          <h2 className="text-xl font-medium text-center mb-6 text-gray-500">Find Recipes With Your Ingredients</h2>
          
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
            <p>Enter ingredients separated by commas (e.g., "chicken, rice, garlic")</p>
            <p className="mt-2 text-green-600">We'll also suggest recipes you can make with alternatives!</p>
          </div>
        </div>
      </div>
      
      {showModal && renderRecipeModal()}
    </div>
  )
}

export default IngredientRecommendationPage