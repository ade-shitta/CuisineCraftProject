"use client"

import React from "react"

interface AllergyItemProps {
  name: string
  image: string
  isSelected: boolean
  onToggle: (name: string) => void
  onError?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
}

const AllergyItem = ({ name, image, isSelected, onToggle, onError }: AllergyItemProps) => {
  return (
    <div
      className={`flex flex-col items-center cursor-pointer ${isSelected ? "opacity-50" : ""}`}
      onClick={() => onToggle(name)}
    >
      <div className="relative mb-1">
        <img 
          src={image || "/placeholder.svg"} 
          alt={name} 
          className="w-16 h-16 rounded-lg object-cover"
          onError={onError} 
        />
        {isSelected && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-lg">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )}
      </div>
      <span className="text-xs text-center">{name}</span>
    </div>
  )
}

export default AllergyItem