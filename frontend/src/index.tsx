import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import { recommendations } from './services/api';

// Lazy load the App component
const App = React.lazy(() => import('./App'));

// Initialize app with authentication-aware data loading
const initializeApp = async () => {
  try {
    // This will handle the authentication check internally
    await recommendations.prefetchRecommendations(12);
    
    // Other initialization tasks...
  } catch (error) {
    console.error("Error initializing application:", error);
  }
};

initializeApp();

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
