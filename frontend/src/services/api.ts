import axios from 'axios';
import { getCSRFToken, setCSRFTokenHeader, fetchCSRFToken } from './csrf';
import Cookies from 'js-cookie';
import { cacheService } from './cache';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // Critical for cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add response interceptor to detect authentication issues
api.interceptors.response.use(
  response => response,
  error => {
    // If we get a 401 or 403, it means our session might have expired
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // Clear user from localStorage if auth error occurs
      localStorage.removeItem('user');
      // We could also redirect to login here, but that would interrupt the user flow
    }
    return Promise.reject(error);
  }
);

// Request interceptor to add CSRF token to requests
api.interceptors.request.use(async (config) => {
  // For non-GET methods, ensure we have a CSRF token
  if (config.method !== 'get') {
    // Check if we have a CSRF token already
    if (!getCSRFToken()) {
      // If no token exists, fetch one first
      await fetchCSRFToken();
    }
    // Add the token to the request
    return setCSRFTokenHeader(config);
  }
  return config;
});

// Auth API
export const auth = {
  register: (userData: any) => api.post('/api/register/', userData),
  login: (username: string, password: string) => api.post('/api/login/', { username, password }),
  logout: () => api.post('/api/logout/'),
  getProfile: () => api.get('/api/profile/'),
  updateProfile: (formData: FormData) => api.post('/api/profile/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  checkIsAuthenticated: async () => {
    try {
      const response = await api.get('/api/authenticated/');
      return response.data.isAuthenticated;
    } catch (error) {
      console.error("Failed to check authentication status:", error);
      return false;
    }
  },
};

// Recipes API with caching
export const recipes = {
  getAll: async () => {
    const cacheKey = 'recipes:all';
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get('/recipes/api/');
    cacheService.set(cacheKey, response.data);
    return response;
  },
  
  getById: async (id: string) => {
    const cacheKey = `recipes:${id}`;
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get(`/recipes/api/${id}/`);
    cacheService.set(cacheKey, response.data);
    return response;
  },
  
  getFavorites: async () => {
    const cacheKey = 'recipes:favorites';
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get('/recipes/api/favorites/');
    cacheService.set(cacheKey, response.data);
    return response;
  },
  
  toggleFavorite: async (id: string) => {
    const response = await api.post(`/recipes/api/${id}/toggle-favorite/`);
    // Invalidate caches that would be affected
    cacheService.invalidate('recipes:all');
    cacheService.invalidate(`recipes:${id}`);
    cacheService.invalidate('recipes:favorites');
    // Invalidate recommendations cache as toggling favorites affects recommendations
    cacheService.invalidate(/^recommendations:recommended/);
    return response;
  },
  
  search: async (query: string) => {
    const cacheKey = `recipes:search:${query}`;
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get(`/recipes/api/search/?q=${encodeURIComponent(query)}`);
    cacheService.set(cacheKey, response.data);
    return response;
  },
  
  searchByIngredients: async (ingredients: string) => {
    const cacheKey = `recipes:search:ingredients:${ingredients}`;
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get(`/recipes/api/search/?ingredients=${encodeURIComponent(ingredients)}`);
    cacheService.set(cacheKey, response.data, 300); // 5 minute cache
    return response;
  },
  
  getAlmostMatchingRecipes: async (ingredients: string, maxMissing = 2, limit = 10) => {
    const cacheKey = `recipes:almost-matching:${ingredients}:${maxMissing}:${limit}`;
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get(
      `/recommendations/api/almost-matching/?ingredients=${encodeURIComponent(ingredients)}` +
      `&max_missing=${maxMissing}&limit=${limit}`
    );
    cacheService.set(cacheKey, response.data, 300); // 5 minute cache
    return response;
  },
  
  markRecipeCooked: async (recipeId: string) => {
    console.log(`Calling API with URL: /recipes/api/${recipeId}/cook/`);
    try {
      const response = await api.post(`/recipes/api/${recipeId}/cook/`);
      return response.data;
    } catch (error) {
      console.error(`Full API request URL: ${api.defaults.baseURL}/recipes/api/${recipeId}/cook/`);
      throw error;
    }
  },
};

// Ingredients API
export const ingredients = {
  getAll: () => api.get('/ingredients/api/'),
  getUserIngredients: () => api.get('/ingredients/api/user/'),
  trackIngredient: (id: string) => api.post(`/ingredients/api/${id}/track/`),
  untrackIngredient: (id: string) => api.post(`/ingredients/api/${id}/untrack/`),
};

// Recommendations API
export const recommendations = {
  getDietaryPreferences: () => api.get('/recommendations/api/preferences/'),
  updateDietaryPreferences: (preferences: string[]) => {
    const response = api.post('/recommendations/api/preferences/', { preferences });
    // Clear all recipe caches as dietary preferences affect recipe filtering
    cacheService.invalidate(/^recipes:/);
    cacheService.invalidate(/^recommendations:/);
    return response;
  },
  getRecommended: async (limit = 12) => {
    const cacheKey = `recommendations:recommended:${limit}`;
    const cached = cacheService.get(cacheKey);
    
    if (cached) return { data: cached };
    
    const response = await api.get(`/recommendations/api/recommended/?limit=${limit}`);
    // Cache for a longer time since we've increased the TTL in the cache service
    cacheService.set(cacheKey, response.data);
    return response;
  },
  // Adding function to explicitly refresh recommendations
  refreshRecommendations: async (limit = 12) => {
    // Invalidate the cache first
    cacheService.invalidate(/^recommendations:recommended/);
    // Then fetch fresh data
    const response = await api.get(`/recommendations/api/recommended/?limit=${limit}`);
    cacheService.set(`recommendations:recommended:${limit}`, response.data);
    return response;
  },
  // New method to prefetch recommendations when app loads
  prefetchRecommendations: async (limit = 12) => {
    try {
      // Check if user is authenticated first
      const isAuthenticated = await auth.checkIsAuthenticated();
      if (!isAuthenticated) {
        console.log("Skipping recommendations prefetch for unauthenticated user");
        return;
      }
      
      // Continue with prefetch for authenticated users
      const cacheKey = `recommendations:recommended:${limit}`;
      await cacheService.prefetch(
        cacheKey,
        () => api.get(`/recommendations/api/recommended/?limit=${limit}`)
      );
    } catch (error) {
      console.warn("Failed to prefetch recommendations:", error);
    }
  }
};

export default api;