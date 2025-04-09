"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import Tooltip from "./Tooltip"

interface RecipeCardProps {
  id: string
  title: string
  image: string
  isFavorite?: boolean
  onToggleFavorite?: (id: string) => void
}

const RecipeCard = ({ id, title, image, isFavorite = false, onToggleFavorite }: RecipeCardProps) => {
  const navigate = useNavigate()
  const [favorite, setFavorite] = useState(isFavorite)
  const [isHovering, setIsHovering] = useState(false)
  const [isAnimating, setIsAnimating] = useState(false)

  // Update local state when prop changes (to handle parent component state updates)
  useEffect(() => {
    setFavorite(isFavorite)
  }, [isFavorite])

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    
    // Animate heart
    setIsAnimating(true)
    setTimeout(() => setIsAnimating(false), 300)
    
    // Only update local state after the callback completes
    if (onToggleFavorite) {
      onToggleFavorite(id)
      // Let the parent component control the state
      // setFavorite will be triggered by the useEffect when the prop changes
    }
  }

  return (
    <div 
      className="relative rounded-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:shadow-lg hover:scale-105" 
      onClick={() => navigate(`/recipe/${id}`)}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className="overflow-hidden">
        <img 
          src={image || "/placeholder.svg"} 
          alt={title} 
          className={`w-full h-32 object-cover transition-all duration-500 ${isHovering ? 'scale-110' : 'scale-100'}`}
        />
      </div>
      
      <Tooltip text={favorite ? "Remove from favorites" : "Add to favorites"}>
        <button
          className={`absolute top-2 right-2 bg-white/90 rounded-full p-1.5 shadow-md hover:bg-pink-100 transition-all duration-300 ${isAnimating ? 'animate-pulse' : ''}`}
          onClick={handleFavoriteClick}
          aria-label={favorite ? "Remove from favorites" : "Add to favorites"}
        >
          {favorite ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`h-5 w-5 text-red-500 transition-transform duration-300 ${isAnimating ? 'scale-125' : ''}`}
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`h-5 w-5 text-gray-500 transition-transform duration-300 ${isAnimating ? 'scale-125' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
          )}
        </button>
      </Tooltip>
      
      <div className={`bg-white p-2 text-center transition-all duration-300 ${isHovering ? 'bg-gray-50' : ''}`}>
        <p className="text-sm font-medium">{title}</p>
      </div>
    </div>
  )
}

export default RecipeCard