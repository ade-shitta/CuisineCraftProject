import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

interface PageTransitionProps {
  children: React.ReactNode;
}

const PageTransition: React.FC<PageTransitionProps> = ({ children }) => {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState('fadeIn');
  
  useEffect(() => {
    if (location.pathname !== displayLocation.pathname) {
      setTransitionStage('fadeOut');
      
      const timeout = setTimeout(() => {
        setDisplayLocation(location);
        setTransitionStage('fadeIn');
      }, 300); // Match this with your transition duration
      
      return () => clearTimeout(timeout);
    }
  }, [location, displayLocation]);
  
  return (
    <div 
      className={`transition-all duration-300 ${
        transitionStage === 'fadeIn' ? 'opacity-100' : 'opacity-0'
      }`}
      style={{ 
        transform: transitionStage === 'fadeIn' ? 'translateY(0)' : 'translateY(20px)',
        minHeight: '100vh'
      }}
    >
      {children}
    </div>
  );
};

export default PageTransition; 