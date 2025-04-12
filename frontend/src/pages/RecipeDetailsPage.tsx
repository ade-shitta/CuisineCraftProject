"use client"

import { useEffect, useState, useCallback } from "react"
import { useParams, useNavigate, useLocation } from "react-router-dom"
import Header from "../components/Header"
import { recipes } from "../services/api"
import { useAuth } from "../context/AuthContext"
import React from 'react'
import LoadingSpinner from '../components/LoadingSpinner'
import RecipeInstructions from "../components/RecipeInstructions"

// Type definitions
type Ingredient = {
  name: string;
  amount: string;
};

type Recipe = {
  recipe_id: string;
  title: string;
  image_url?: string;
  ingredients: Ingredient[];
  instructions: string[];
  isFavorite: boolean;
  dietary_tags: string[];
}

// Memoize UI components
const DietaryTags: React.FC<{ tags: string[] }> = React.memo(({ tags }) => (
  <div className="mb-6 text-center">
    <h2 className="text-xl font-bold text-black mb-4">Dietary Tags</h2>
    <div className="flex flex-wrap justify-center gap-2">
      {tags.map((tag, index) => (
        <span
          key={index}
          className="bg-red-300 text-black px-4 py-2 rounded-full text-sm font-medium shadow-sm"
        >
          {tag}
        </span>
      ))}
    </div>
  </div>
));

const IngredientList: React.FC<{ ingredients: Ingredient[] }> = React.memo(({ ingredients }) => (
  <div className="grid grid-cols-2 gap-4 mx-auto max-w-xl">
    {ingredients.map((ingredient, index) => (
      <div key={index} className="bg-red-200 rounded-3xl p-4 flex justify-between items-center">
        <p className="text-black font-medium">{ingredient.name}</p>
        <p className="text-black">{ingredient.amount}</p>
      </div>
    ))}
  </div>
));

interface InstructionModalProps {
  isOpen: boolean;
  onClose: () => void;
  instructions: string[];
  recipeId: string;
}

const InstructionModal: React.FC<InstructionModalProps> = React.memo(({ isOpen, onClose, instructions, recipeId }) => {
  const [completionStatus, setCompletionStatus] = useState({
    isCompleted: false,
    isSubmitting: false,
    error: null as string | null
  });
  
  if (!isOpen) return null;
  
  const handleCookCompleted = async (recipeId: string) => {
    try {
      setCompletionStatus(prev => ({ ...prev, isSubmitting: true }));
      
      // Pass recipeId as string directly
      await recipes.markRecipeCooked(recipeId);
      
      setCompletionStatus({
        isCompleted: true,
        isSubmitting: false,
        error: null
      });
      
    } catch (error) {
      console.error("Failed to record recipe completion:", error);
      setCompletionStatus({
        isCompleted: false,
        isSubmitting: false,
        error: "Failed to record your cooking achievement. Please try again."
      });
    }
  };
  
  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-bold text-gray-800">Recipe Instructions</h2>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100 p-1"
            aria-label="Close"
            title="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-4">
          <RecipeInstructions 
            rawInstructions={instructions}
            recipeId={recipeId}
            onComplete={handleCookCompleted} 
          />
          
          {completionStatus.error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
              {completionStatus.error}
            </div>
          )}
        </div>
        
        <div className="border-t p-4 flex justify-end">
          <button 
            onClick={onClose}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-full"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
});

const RecipeDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showLoader, setShowLoader] = useState(false);

  useEffect(() => {
    if (!id || !isAuthenticated) return;

    setLoading(true);
    const loaderTimer = setTimeout(() => {
      if (loading) setShowLoader(true);
    }, 300);

    const fetchRecipe = async () => {
      try {
        const response = await recipes.getById(id);
        
        const instructions = response.data.instructions.split('\n').filter(Boolean);
        const ingredients = Array.isArray(response.data.ingredients) 
          ? response.data.ingredients 
          : [];
        
        setRecipe({
          ...response.data,
          instructions,
          ingredients,
          dietary_tags: response.data.dietary_tags || []
        });
        setLoading(false);
      } catch (err) {
        console.error("Error fetching recipe:", err);
        setError("Failed to load recipe");
        setLoading(false);
      } finally {
        setShowLoader(false);
      }
    };

    fetchRecipe();
    return () => clearTimeout(loaderTimer);
  }, [id, isAuthenticated, location.key]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate("/login");
    }
  }, [authLoading, isAuthenticated, navigate]);

  const handleModalOpen = useCallback(() => setShowModal(true), []);
  const handleModalClose = useCallback(() => setShowModal(false), []);
  const handleBackClick = useCallback(() => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/home');
    }
  }, [navigate]);

  const handleToggleFavorite = useCallback(async () => {
    if (!recipe) return;
    
    try {
      await recipes.toggleFavorite(recipe.recipe_id);
      setRecipe(prev => prev ? { ...prev, isFavorite: !prev.isFavorite } : null);
    } catch (error) {
      console.error("Error toggling favorite:", error);
    }
  }, [recipe]);

  if ((authLoading || loading) && showLoader) {
    return <LoadingSpinner />;
  }

  if (error || !recipe) {
    return (
      <div className="min-h-screen bg-red-400 flex justify-center items-center">
        <p className="text-white">{error || "Recipe not found"}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1">
          <button 
            onClick={handleBackClick}
            className="bg-red-500 hover:bg-red-600 text-white rounded-full w-10 h-10 flex items-center justify-center shadow-md"
            aria-label="Go back"
            title="Go back"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">{recipe.title}</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      <div className="flex justify-center mb-8 px-6 relative">
        {recipe.image_url && (
          <div className="relative inline-block">
            <img
              src={recipe.image_url}
              alt={recipe.title}
              className="rounded-3xl w-full max-w-md h-44 object-cover shadow-md"
              loading="eager"
            />
            <button 
              className="absolute top-3 right-3 bg-pink-100 rounded-full p-2 shadow-md"
              onClick={handleToggleFavorite}
              aria-label={recipe.isFavorite ? "Remove from favorites" : "Add to favorites"}
              title={recipe.isFavorite ? "Remove from favorites" : "Add to favorites"}
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className={`h-6 w-6 ${recipe.isFavorite ? 'text-red-500' : 'text-gray-400'}`}
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
          </div>
        )}
      </div>

      <div className="px-6 pb-16">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-xl font-bold text-black">Ingredients</h2>
          <a 
            href="#"
            onClick={(e) => {
              e.preventDefault();
              handleModalOpen();
            }}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            View Recipe Details
          </a>
        </div>

        {recipe.ingredients?.length > 0 ? (
          <div className="bg-red-300 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">Ingredients</h3>
            <ul className="space-y-2">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-black text-lg mr-2">•</span>
                  <span className="text-black text-lg">
                    {ingredient.amount ? `${ingredient.amount} of ${ingredient.name}` : ingredient.name}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="bg-red-300 rounded-xl p-6 text-center">
            <p className="text-black">No ingredients available for this recipe</p>
          </div>
        )}
      </div>

      {showModal && (
        <InstructionModal 
          isOpen={showModal}
          onClose={handleModalClose}
          instructions={recipe?.instructions || []}
          recipeId={recipe?.recipe_id || ''}
        />
      )}
    </div>
  );
};

export default React.memo(RecipeDetailsPage);