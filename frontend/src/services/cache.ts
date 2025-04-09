// Simple in-memory cache for API responses
type CacheEntry = {
  data: any;
  expiry: number;
  key: string;
};

const cache = new Map<string, CacheEntry>();

// Track the last 10 invalidated caches for debugging
const recentInvalidations: string[] = [];

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
  
  set: (key: string, data: any, ttlSeconds = 300) => {
    const expiry = Date.now() + (ttlSeconds * 1000);
    cache.set(key, { data, expiry, key });
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