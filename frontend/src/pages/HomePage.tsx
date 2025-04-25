import { useState, useEffect, useRef } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import RecipeCard from "../components/RecipeCard"
import { recipes, recommendations } from "../services/api"
import { ApiRecipe } from "../types/api"

const RecipeCardSkeleton = () => (
  <div className="flex-shrink-0 transform w-40 h-40">
    <div className="relative w-40 h-40 rounded-xl overflow-hidden shadow-md bg-gray-200 animate-pulse">
      <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-xl py-2">
        <div className="w-3/4 h-4 bg-gray-200 mx-auto"></div>
      </div>
    </div>
  </div>
);

const HomePage = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [searchQuery, setSearchQuery] = useState("")
  const [recipeData, setRecipeData] = useState<any[]>([])
  const [recommendedRecipes, setRecommendedRecipes] = useState<any[]>([])
  const [favorites, setFavorites] = useState<any[]>([])
  
  const [loadingRecommendations, setLoadingRecommendations] = useState(true)
  const [loadingFavorites, setLoadingFavorites] = useState(true)
  
  const discoverScrollRef = useRef<HTMLDivElement>(null)
  const favoritesScrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login")
      return
    }
  }, [isAuthenticated, navigate, isLoading])

  const fetchRecommendations = async () => {
    if (!isAuthenticated) return;
    
    setLoadingRecommendations(true);
    try {
      const recommendedResponse = await recommendations.getRecommended(12);
      
      setRecommendedRecipes(recommendedResponse.data.map((recipe: ApiRecipe) => ({
        id: recipe.recipe_id,
        title: recipe.title,
        image: recipe.image_url,
        isFavorite: recipe.isFavorite
      })));
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoadingRecommendations(false);
    }
  }
  
  const fetchFavorites = async () => {
    if (!isAuthenticated) return;
    
    setLoadingFavorites(true);
    try {
      const favoritesResponse = await recipes.getFavorites();
      
      setFavorites(favoritesResponse.data.map((recipe: ApiRecipe) => ({
        id: recipe.recipe_id,
        title: recipe.title,
        image: recipe.image_url,
        isFavorite: true
      })));
    } catch (error) {
      console.error("Error fetching favorites:", error);
    } finally {
      setLoadingFavorites(false);
    }
  }

  useEffect(() => {
    if (!isAuthenticated) {
      return
    }

    fetchRecommendations();
    fetchFavorites();
  }, [isAuthenticated, navigate, location.key, user?.id])

  useEffect(() => {
    // Create a set of favorite recipe IDs for quick lookup
    const favoriteIds = new Set(favorites.map(recipe => recipe.id));
    
    // Update recommended recipes to match favorite status
    setRecommendedRecipes(prevRecipes => 
      prevRecipes.map(recipe => ({
        ...recipe,
        isFavorite: favoriteIds.has(recipe.id)
      }))
    );
  }, [favorites]);

  const handleToggleFavorite = async (id: string) => {
    try {
      await recipes.toggleFavorite(id);
      
      setRecipeData(prevRecipes => 
        prevRecipes.map(recipe => 
          recipe.id === id 
            ? { ...recipe, isFavorite: !recipe.isFavorite } 
            : recipe
        )
      );
      
      setRecommendedRecipes(prevRecipes => 
        prevRecipes.map(recipe => 
          recipe.id === id 
            ? { ...recipe, isFavorite: !recipe.isFavorite } 
            : recipe
        )
      );
      
      const wasInFavorites = favorites.some(recipe => recipe.id === id);
      if (wasInFavorites) {
        setFavorites(prevFavorites => 
          prevFavorites.filter(recipe => recipe.id !== id)
        );
      } else {
        const favoritesResponse = await recipes.getFavorites();
        setFavorites(favoritesResponse.data.map((recipe: ApiRecipe) => ({
          id: recipe.recipe_id,
          title: recipe.title,
          image: recipe.image_url,
          isFavorite: true
        })));
      }
      
      setTimeout(async () => {
        try {
          const newRecommendations = await recommendations.refreshRecommendations(12);
          setRecommendedRecipes(newRecommendations.data.map((recipe: ApiRecipe) => ({
            id: recipe.recipe_id,
            title: recipe.title,
            image: recipe.image_url,
            isFavorite: recipe.isFavorite
          })));
        } catch (error) {
          console.error("Error refreshing recommendations:", error);
        }
      }, 500);
    } catch (error) {
      console.error("Error toggling favorite:", error);
    }
  }
  
  const scrollRecipes = (ref: { current: HTMLDivElement | null }, direction: 'left' | 'right') => {
    if (!ref.current) return;
    
    const scrollContainer = ref.current;
    
    scrollContainer.style.scrollBehavior = 'auto';
    
    const cardWidth = 128; 
    const marginRight = 16; 
    const scrollAmount = cardWidth + marginRight;
    
    const newPosition = direction === 'left'
      ? scrollContainer.scrollLeft - scrollAmount
      : scrollContainer.scrollLeft + scrollAmount;
    
    setTimeout(() => {
      scrollContainer.style.scrollBehavior = 'smooth';
      scrollContainer.scrollLeft = newPosition;
    }, 0);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-red-400 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg text-white"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1"></div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Hi! {user?.username || "Guest"}</h1>
          <p className="text-white/80 mt-1">What are we cooking today?</p>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      <div className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <button 
            onClick={() => navigate('/recipes')} 
            className="btn bg-red-500 hover:bg-red-600 text-white border-none flex items-center hover:scale-105 transition-all duration-300 hover:shadow-lg"
          >
            Discover Recipes
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
          <button 
            className="btn btn-circle btn-sm bg-red-500 hover:bg-red-600 text-white border-none hover:scale-110 transition-all duration-300 hover:shadow-lg"
            onClick={() => scrollRecipes(discoverScrollRef, 'right')}
            aria-label="Scroll discover recipes right"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        <div 
          ref={discoverScrollRef} 
          className="flex gap-4 overflow-x-auto hide-scrollbar"
          style={{ scrollBehavior: 'smooth' }}
        >
          {loadingRecommendations ? (
            Array(6).fill(0).map((_, index) => (
              <RecipeCardSkeleton key={`skeleton-${index}`} />
            ))
          ) : (
            recommendedRecipes.map((recipe) => (
              <div className="flex-shrink-0 transform transition duration-300 hover:scale-105" key={recipe.id}>
                <div className="relative w-40 h-40 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-all">
                  <img 
                    src={recipe.image} 
                    alt={recipe.title} 
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
                    onClick={() => navigate(`/recipe/${recipe.id}`)}
                    loading="lazy" 
                  />
                  <button 
                    className="absolute top-2 right-2 bg-pink-100 rounded-full p-1.5 shadow-sm hover:bg-pink-200 transition-colors duration-300"
                    onClick={() => handleToggleFavorite(recipe.id)}
                    aria-label={recipe.isFavorite ? "Remove from favorites" : "Add to favorites"}
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
                  <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-xl py-2">
                    <p className="text-center text-gray-800 font-medium text-sm">{recipe.title}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <button 
            onClick={() => navigate('/favorites')} 
            className="btn bg-red-500 hover:bg-red-600 text-white border-none flex items-center hover:scale-105 transition-all duration-300 hover:shadow-lg"
          >
            My Favorites
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
          <button 
            className="btn btn-circle btn-sm bg-red-500 hover:bg-red-600 text-white border-none hover:scale-110 transition-all duration-300 hover:shadow-lg"
            onClick={() => scrollRecipes(favoritesScrollRef, 'right')}
            aria-label="Scroll favorites right"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        <div 
          ref={favoritesScrollRef}
          className="flex overflow-x-auto hide-scrollbar gap-4"
          style={{ scrollBehavior: 'smooth' }}
        >
          {loadingFavorites ? (
            Array(4).fill(0).map((_, index) => (
              <RecipeCardSkeleton key={`skeleton-fav-${index}`} />
            ))
          ) : (
            favorites.slice(0, 12).map((recipe) => (
              <div className="flex-shrink-0 transform transition duration-300 hover:scale-105" key={recipe.id}>
                <div className="relative w-40 h-40 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-all">
                  <img 
                    src={recipe.image} 
                    alt={recipe.title} 
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
                    onClick={() => navigate(`/recipe/${recipe.id}`)}
                    loading="lazy" 
                  />
                  <button 
                    className="absolute top-2 right-2 bg-pink-100 rounded-full p-1.5 shadow-sm hover:bg-pink-200 transition-colors duration-300"
                    onClick={() => handleToggleFavorite(recipe.id)}
                    aria-label="Remove from favorites"
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
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default HomePage