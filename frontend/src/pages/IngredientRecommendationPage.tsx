"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import { ingredients as ingredientsApi } from "../services/api"

type Ingredient = {
  id: string;
  name: string;
  category: string;
  image_url?: string;
  isTracked: boolean;
}

const IngredientRecommendationPage = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const [ingredients, setIngredients] = useState<Ingredient[]>([])
  const [userIngredients, setUserIngredients] = useState<Ingredient[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Only redirect if we're done loading and not authenticated
    if (!isLoading && !isAuthenticated) {
      navigate("/login")
      return
    }

    const fetchData = async () => {
      try {
        // Fetch all ingredients and user's tracked ingredients
        const [allIngredientsRes, userIngredientsRes] = await Promise.all([
          ingredientsApi.getAll(),
          ingredientsApi.getUserIngredients()
        ])
        
        setIngredients(allIngredientsRes.data)
        setUserIngredients(userIngredientsRes.data)
        setLoading(false)
      } catch (error) {
        console.error("Error fetching ingredients:", error)
        setLoading(false)
      }
    }

    fetchData()
  }, [isAuthenticated, navigate, isLoading])

  const handleToggleTracking = async (ingredient: Ingredient) => {
    try {
      if (ingredient.isTracked) {
        await ingredientsApi.untrackIngredient(ingredient.id)
      } else {
        await ingredientsApi.trackIngredient(ingredient.id)
      }

      // Update local state
      setIngredients(ingredients.map(ing => 
        ing.id === ingredient.id 
          ? { ...ing, isTracked: !ing.isTracked } 
          : ing
      ))

      // Update user ingredients list
      if (ingredient.isTracked) {
        setUserIngredients(userIngredients.filter(ing => ing.id !== ingredient.id))
      } else {
        setUserIngredients([...userIngredients, { ...ingredient, isTracked: true }])
      }
    } catch (error) {
      console.error("Error toggling ingredient tracking:", error)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-red-400 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg text-white"></div>
      </div>
    )
  }

  if (loading) {
    return <div className="min-h-screen bg-red-400 p-4 flex items-center justify-center">
      <span className="loading loading-spinner loading-lg text-white"></span>
    </div>
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1"></div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Ingredients</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      <div className="mb-6">
        <h1 className="text-white text-xl font-bold mb-4">Your Ingredients</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {userIngredients.length > 0 ? (
            userIngredients.map(ingredient => (
              <div key={ingredient.id} className="bg-red-300 rounded-lg p-4 flex flex-col items-center">
                {ingredient.image_url && (
                  <img 
                    src={ingredient.image_url} 
                    alt={ingredient.name} 
                    className="w-16 h-16 object-cover rounded-full mb-2"
                  />
                )}
                <p className="text-white text-center mb-2">{ingredient.name}</p>
                <button
                  onClick={() => handleToggleTracking(ingredient)}
                  className="btn btn-xs bg-red-500 hover:bg-red-600 text-white border-none"
                >
                  Remove
                </button>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center text-white">
              You haven't added any ingredients yet.
            </div>
          )}
        </div>
      </div>

      <div>
        <h1 className="text-white text-xl font-bold mb-4">All Ingredients</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {ingredients.map(ingredient => (
            <div key={ingredient.id} className="bg-red-300 rounded-lg p-4 flex flex-col items-center">
              {ingredient.image_url && (
                <img 
                  src={ingredient.image_url} 
                  alt={ingredient.name} 
                  className="w-16 h-16 object-cover rounded-full mb-2"
                />
              )}
              <p className="text-white text-center mb-2">{ingredient.name}</p>
              <button
                onClick={() => handleToggleTracking(ingredient)}
                className={`btn btn-xs ${
                  ingredient.isTracked 
                  ? "bg-red-500 hover:bg-red-600" 
                  : "bg-green-500 hover:bg-green-600"
                } text-white border-none`}
              >
                {ingredient.isTracked ? "Remove" : "Add"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default IngredientRecommendationPage