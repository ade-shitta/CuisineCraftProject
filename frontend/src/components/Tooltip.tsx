import React, { useState } from 'react';

interface TooltipProps {
  children: React.ReactNode;
  text: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  className?: string;
}

const Tooltip: React.FC<TooltipProps> = ({
  children,
  text,
  position = 'top',
  delay = 300,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [showTimeout, setShowTimeout] = useState<NodeJS.Timeout | null>(null);
  
  const positions = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  };
  
  const handleMouseEnter = () => {
    const timeout = setTimeout(() => {
      setIsVisible(true);
    }, delay);
    setShowTimeout(timeout);
  };
  
  const handleMouseLeave = () => {
    if (showTimeout) {
      clearTimeout(showTimeout);
      setShowTimeout(null);
    }
    setIsVisible(false);
  };
  
  return (
    <div 
      className={`relative inline-block ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
    >
      {children}
      {isVisible && (
        <div 
          className={`absolute ${positions[position]} z-50 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg shadow-sm opacity-0 animate-fade-in pointer-events-none whitespace-nowrap`}
          style={{
            animationDuration: '0.2s',
            animationFillMode: 'forwards',
          }}
        >
          {text}
          <div 
            className={`absolute ${
              position === 'top' ? 'top-full left-1/2 transform -translate-x-1/2 border-t-gray-900' : 
              position === 'bottom' ? 'bottom-full left-1/2 transform -translate-x-1/2 border-b-gray-900' :
              position === 'left' ? 'left-full top-1/2 transform -translate-y-1/2 border-l-gray-900' :
              'right-full top-1/2 transform -translate-y-1/2 border-r-gray-900'
            } w-0 h-0 border-4 border-transparent`}
          />
        </div>
      )}
    </div>
  );
};

export default Tooltip; 