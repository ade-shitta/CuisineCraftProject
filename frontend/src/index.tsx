import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import { recommendations } from './services/api';

// Lazy load the App component
const App = React.lazy(() => import('./App'));

// Prefetch recommendations data as soon as the app loads
// This will run in the background and populate the cache
if (navigator.onLine) {
  recommendations.prefetchRecommendations().catch(err => {
    // Silent fail - we'll fetch on demand if prefetch fails
    console.debug('Background prefetch failed:', err);
  });
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <React.Suspense fallback={<div>Loading...</div>}>
      <App />
    </React.Suspense>
  </React.StrictMode>
);

// Only measure performance in non-production environments
if (process.env.NODE_ENV !== 'production') {
  reportWebVitals();
}
