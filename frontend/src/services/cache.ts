// Simple in-memory cache for API responses
type CacheEntry = {
  data: any;
  expiry: number;
  key: string;
};

const cache = new Map<string, CacheEntry>();

// Track the last 10 invalidated caches for debugging
const recentInvalidations: string[] = [];

// Default cache durations based on content type
const DEFAULT_TTL = 300; // 5 minutes for general content
const RECOMMENDATIONS_TTL = 600; // 10 minutes for recommendations
const FAVORITES_TTL = 300; // 5 minutes for favorites

export const cacheService = {
  get: (key: string) => {
    const cachedItem = cache.get(key);
    if (!cachedItem) return null;
    
    // Check if cache has expired
    if (Date.now() > cachedItem.expiry) {
      cache.delete(key);
      return null;
    }
    
    return cachedItem.data;
  },
  
  set: (key: string, data: any, ttlSeconds = DEFAULT_TTL) => {
    // Apply longer TTL for recommendations automatically
    if (key.startsWith('recommendations:')) {
      ttlSeconds = RECOMMENDATIONS_TTL;
    }
    
    const expiry = Date.now() + (ttlSeconds * 1000);
    cache.set(key, { data, expiry, key });
  },
  
  prefetch: async (key: string, fetchFn: () => Promise<any>, ttlSeconds = DEFAULT_TTL) => {
    // Check if we already have a valid cached entry
    const existingEntry = cache.get(key);
    if (existingEntry && Date.now() < existingEntry.expiry) {
      return existingEntry.data;
    }
    
    try {
      // Fetch the data
      const response = await fetchFn();
      // Store it in cache
      const data = response.data || response;
      cacheService.set(key, data, ttlSeconds);
      return data;
    } catch (error) {
      console.error(`Error prefetching ${key}:`, error);
      throw error;
    }
  },
  
  invalidate: (keyOrPattern: string | RegExp) => {
    if (typeof keyOrPattern === 'string') {
      // Simple key invalidation
      cache.delete(keyOrPattern);
      // Track invalidation for debugging
      recentInvalidations.unshift(keyOrPattern);
    } else {
      // Pattern-based invalidation
      const keys = Array.from(cache.keys());
      const invalidatedKeys: string[] = [];
      
      for (const key of keys) {
        if (keyOrPattern.test(key)) {
          cache.delete(key);
          invalidatedKeys.push(key);
        }
      }
      
      // Track invalidations for debugging
      if (invalidatedKeys.length > 0) {
        recentInvalidations.unshift(`Pattern: ${keyOrPattern} → [${invalidatedKeys.join(', ')}]`);
      }
    }
    
    // Keep only the last 10 invalidations
    if (recentInvalidations.length > 10) {
      recentInvalidations.length = 10;
    }
  },
  
  getDebugInfo: () => {
    return {
      cacheSize: cache.size,
      cacheKeys: Array.from(cache.keys()),
      recentInvalidations: [...recentInvalidations]
    };
  },
  
  clear: () => {
    cache.clear();
    recentInvalidations.length = 0;
  }
};