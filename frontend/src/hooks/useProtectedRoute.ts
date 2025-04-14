import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

// Custom hook to handle auth redirects
export function useProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, isLoading, navigate])
  
  return { isAuthenticated, isLoading }
} 