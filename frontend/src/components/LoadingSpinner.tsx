import React from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  color = 'white',
  message
}) => {
  const textSize = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl'
  };
  
  const dotSize = {
    sm: '8px',
    md: '10px',
    lg: '12px'
  };

  return (
    <div className="min-h-screen bg-red-400 flex flex-col items-center justify-center">
      <div className="flex flex-col items-center">
        {/* Bouncing dots animation only */}
        <div className="flex space-x-3">
          {[...Array(3)].map((_, i) => (
            <div 
              key={i} 
              className={`bg-${color} rounded-full animate-bounce`}
              style={{ 
                width: dotSize[size],
                height: dotSize[size],
                animationDelay: `${i * 0.1}s`
              }}
            ></div>
          ))}
        </div>
        
        {message && (
          <div className={`mt-4 text-${color} ${textSize[size]} font-medium loading-dots`}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}

export default React.memo(LoadingSpinner)