

import { useState, useEffect, useCallback, useMemo } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import { recipes } from "../services/api"
import { ApiRecipe } from "../types/api"
import React from 'react'
import LoadingSpinner from '../components/LoadingSpinner'

// Recipe item type for internal usage
interface RecipeItem {
  id: string;
  title: string;
  image?: string;
  isFavorite: boolean;
}

interface RecipeCardProps {
  recipe: RecipeItem;
  onToggleFavorite: (id: string) => void;
  onCardClick: (id: string) => void;
}

// Memoize recipe card component
const RecipeCard: React.FC<RecipeCardProps> = React.memo(({ recipe, onToggleFavorite, onCardClick }) => {
  const handleToggle = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite(recipe.id);
  }, [recipe.id, onToggleFavorite]);

  const handleClick = useCallback(() => {
    onCardClick(recipe.id);
  }, [recipe.id, onCardClick]);

  return (
    <div className="flex-shrink-0 transform transition duration-300 hover:scale-105">
      <div className="relative w-full aspect-square rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-all">
        <img 
          src={recipe.image || "/placeholder.svg"} 
          alt={recipe.title} 
          className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
          loading="lazy" // Lazy load images that might be off-screen
          onClick={handleClick}
        />
        <button 
          className="absolute top-2 right-2 bg-pink-100 rounded-full p-1.5 shadow-sm hover:bg-pink-200 transition-colors duration-300"
          onClick={handleToggle}
          aria-label={recipe.isFavorite ? "Remove from favorites" : "Add to favorites"}
          title={recipe.isFavorite ? "Remove from favorites" : "Add to favorites"}
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className={`h-5 w-5 ${recipe.isFavorite ? 'text-red-500' : 'text-gray-400'} transition-colors duration-300`}
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
        <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-xl py-2 transition-colors duration-300 hover:bg-gray-50">
          <p className="text-center text-gray-800 font-medium text-sm">{recipe.title}</p>
        </div>
      </div>
    </div>
  );
});

const RecipesPage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState("");
  const [allRecipes, setAllRecipes] = useState<RecipeItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const recipesPerPage = 12; // 4 columns x 3 rows = 12 recipes per page

  // Fetch recipes when component mounts or when navigating back to the page
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchRecipes = async () => {
      setLoading(true);
      try {
        const response = await recipes.getAll();
        const recipeItems = response.data.map((recipe: ApiRecipe) => ({
          id: recipe.recipe_id,
          title: recipe.title,
          image: recipe.image_url,
          isFavorite: recipe.isFavorite
        }));
        
        setAllRecipes(recipeItems);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching recipes:", error);
        setLoading(false);
      }
    };

    fetchRecipes();
  }, [isAuthenticated, location.key]); // Added location.key to reload data when navigating back

  // Handle user authentication
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate("/login");
    }
  }, [authLoading, isAuthenticated, navigate]);

  // Memoize handlers
  const handleToggleFavorite = useCallback(async (id: string) => {
    try {
      await recipes.toggleFavorite(id);
      
      // Update local state
      setAllRecipes(prev => 
        prev.map(recipe => 
          recipe.id === id 
            ? { ...recipe, isFavorite: !recipe.isFavorite } 
            : recipe
        )
      );
    } catch (error) {
      console.error("Error toggling favorite:", error);
    }
  }, []);

  const handleCardClick = useCallback((id: string) => {
    navigate(`/recipe/${id}`);
  }, [navigate]);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1); // Reset to first page on search
  }, []);

  // Memoize expensive calculations
  const filteredRecipes = useMemo(() => {
    return allRecipes.filter(recipe =>
      recipe.title.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [allRecipes, searchQuery]);

  const paginatedRecipes = useMemo(() => {
    const indexOfLastRecipe = currentPage * recipesPerPage;
    const indexOfFirstRecipe = indexOfLastRecipe - recipesPerPage;
    return filteredRecipes.slice(indexOfFirstRecipe, indexOfLastRecipe);
  }, [filteredRecipes, currentPage, recipesPerPage]);

  const totalPages = useMemo(() => {
    return Math.ceil(filteredRecipes.length / recipesPerPage);
  }, [filteredRecipes.length, recipesPerPage]);

  // Pagination handlers
  const paginate = useCallback((pageNumber: number) => setCurrentPage(pageNumber), []);
  const nextPage = useCallback(() => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  }, [totalPages]);
  
  const prevPage = useCallback(() => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  }, []);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-red-400 flex flex-col items-center justify-center">
        <div className="loading loading-bars loading-lg text-white"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1">
          <button
            onClick={() => navigate('/home')}
            className="bg-red-500 hover:bg-red-600 text-white rounded-full w-10 h-10 flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-300 hover:scale-110"
            aria-label="Back to home"
            title="Back to home"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Recipes</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search recipes..."
              className="input input-bordered max-w-xs focus:ring-2 focus:ring-red-300 focus:border-red-300 transition-all duration-300 hover:border-red-200"
              value={searchQuery}
              onChange={handleSearchChange}
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-red-500 transition-colors duration-300"
                aria-label="Clear search"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>
      
      {allRecipes.length === 0 && !loading ? (
        <div className="bg-white rounded-lg p-6 shadow-md text-center max-w-md mx-auto">
          <h2 className="text-xl font-semibold mb-3">No Matching Recipes</h2>
          <p className="mb-4">No recipes match your dietary preferences.</p>
          <button 
            onClick={() => navigate('/dietary-preferences')}
            className="btn bg-red-500 hover:bg-red-600 text-white border-none hover:scale-105 transition-all duration-300 hover:shadow-lg"
          >
            Update Preferences
          </button>
        </div>
      ) : paginatedRecipes.length > 0 ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mx-auto max-w-6xl mb-8">
            {paginatedRecipes.map((recipe) => (
              <RecipeCard 
                key={recipe.id}
                recipe={recipe}
                onToggleFavorite={handleToggleFavorite}
                onCardClick={handleCardClick}
              />
            ))}
          </div>
          
          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex flex-col items-center gap-2 my-4">
              <div className="flex justify-center gap-2">
                {/* First page button - only show when on page 3 or higher */}
                {currentPage >= 3 && (
                  <button
                    onClick={() => paginate(1)}
                    className="px-4 py-2 rounded-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 hover:scale-105 transition-all duration-300 hover:shadow-md"
                  >
                    « First
                  </button>
                )}
                
                {/* Previous button - only show when not on first page */}
                {currentPage > 1 && (
                  <button
                    onClick={prevPage}
                    className="px-4 py-2 rounded-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 hover:scale-105 transition-all duration-300 hover:shadow-md"
                  >
                    Previous
                  </button>
                )}
                
                {/* Show numbered buttons with a limit */}
                {(() => {
                  const pageButtons = [];
                  const maxVisibleButtons = 5;
                  const halfVisible = Math.floor(maxVisibleButtons / 2);
                  
                  let startPage = Math.max(1, currentPage - halfVisible);
                  let endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1);
                  
                  // Adjust if we're at the end
                  if (endPage - startPage + 1 < maxVisibleButtons) {
                    startPage = Math.max(1, endPage - maxVisibleButtons + 1);
                  }
                  
                  // Generate number buttons
                  for (let i = startPage; i <= endPage; i++) {
                    pageButtons.push(
                      <button
                        key={i}
                        onClick={() => paginate(i)}
                        className={`px-4 py-2 rounded-full border ${
                          currentPage === i 
                            ? "bg-red-500 text-white border-red-500" 
                            : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
                        }`}
                      >
                        {i}
                      </button>
                    );
                  }
                  
                  return pageButtons;
                })()}
                
                {/* Next button - only show when not on last page */}
                {currentPage < totalPages && (
                  <button
                    onClick={nextPage}
                    className="px-4 py-2 rounded-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 hover:scale-105 transition-all duration-300 hover:shadow-md"
                  >
                    Next
                  </button>
                )}
                
                {/* Last button - only show when not on last page AND before or on page 24 */}
                {currentPage < totalPages && currentPage <= 24 && (
                  <button
                    onClick={() => paginate(totalPages)}
                    className="px-4 py-2 rounded-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 hover:scale-105 transition-all duration-300 hover:shadow-md"
                  >
                    Last »
                  </button>
                )}
              </div>
              
              {/* Page info */}
              <div className="text-gray-600 text-sm">
                Page {currentPage} of {totalPages}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center text-white py-8">
          No recipes found matching your search.
        </div>
      )}
    </div>
  );
};

export default React.memo(RecipesPage);