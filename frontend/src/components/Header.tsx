

import { useState, useRef, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

interface HeaderProps {
  showMenu?: boolean
}

const Header = ({ showMenu = true }: HeaderProps) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null) // Add ref for the menu container

  // Determine current path
  const currentPath = location.pathname

  // Handle clicks outside the menu
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }

    // Add event listener when menu is open
    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside)
    }

    // Clean up event listener
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [isMenuOpen])

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <div>
      {showMenu && (
        <div ref={menuRef}>
          <button 
            onClick={toggleMenu} 
            className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md"
            aria-label="Menu"
            title="Menu"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-6 w-6 text-gray-500" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {isMenuOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-20">
              <div className="px-4 py-2 text-sm text-gray-700">Hi, {user?.username || "Guest"}</div>
              <hr className="my-1" />
              
              {/* Show Home button only if not on homepage */}
              {currentPath !== "/home" && (
                <button
                  onClick={() => {
                    navigate("/home")
                    setIsMenuOpen(false)
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Home
                </button>
              )}
              
              {/* Show Profile button only if not on profile page */}
              {currentPath !== "/profile" && (
                <button
                  onClick={() => {
                    navigate("/profile")
                    setIsMenuOpen(false)
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Profile
                </button>
              )}
              
              {/* Always show Search by Ingredient unless on that page */}
              {currentPath !== "/ingredient-recommendations" && (
                <button
                  onClick={() => {
                    navigate("/ingredient-recommendations")
                    setIsMenuOpen(false)
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Search by Ingredient
                </button>
              )}
              
              <hr className="my-1" />
              <button
                onClick={() => {
                  logout()
                  navigate("/")
                  setIsMenuOpen(false)
                }}
                className="block w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-100"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Header