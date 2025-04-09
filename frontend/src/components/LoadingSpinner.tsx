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
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-10 w-10',
    lg: 'h-16 w-16'
  };

  const textSize = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl'
  };

  return (
    <div className="min-h-screen bg-red-400 flex flex-col items-center justify-center">
      <div className="flex flex-col items-center">
        <div className="relative">
          <div className={`${sizeClasses[size]} border-4 border-t-transparent border-${color} rounded-full animate-spin`}></div>
          <div className={`absolute top-0 left-0 ${sizeClasses[size]} border-4 border-t-transparent border-${color} border-opacity-30 rounded-full`}></div>
        </div>
        
        {message && (
          <div className={`mt-4 text-${color} ${textSize[size]} font-medium loading-dots`}>
            {message}
          </div>
        )}
        
        <div className="mt-6 flex space-x-2">
          {[...Array(3)].map((_, i) => (
            <div 
              key={i} 
              className={`bg-${color} rounded-full animate-bounce`}
              style={{ 
                width: size === 'sm' ? '8px' : size === 'md' ? '10px' : '12px',
                height: size === 'sm' ? '8px' : size === 'md' ? '10px' : '12px',
                animationDelay: `${i * 0.1}s`
              }}
            ></div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default React.memo(LoadingSpinner) 