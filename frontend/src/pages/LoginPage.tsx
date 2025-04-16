

import type React from "react"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { fetchCSRFToken } from "../services/csrf"

const LoginPage = () => {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [loginSuccess, setLoginSuccess] = useState(false)

  // Animation on mount
  useEffect(() => {
    document.querySelector('.login-container')?.classList.add('animate-fade-in')
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    // Clear error when user types
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.username) newErrors.username = "Username is required"
    if (!formData.password) newErrors.password = "Password is required"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      try {
        setIsLoading(true);
        // Before login, ensure we have a fresh CSRF token
        await fetchCSRFToken();
        await login(formData.username, formData.password);
        
        // Show success animation before navigating
        setLoginSuccess(true);
        setTimeout(() => {
          navigate("/home");
        }, 800);
      } catch (error: any) {
        console.error("Login error:", error);
        const errorMsg = error.response?.data?.detail || "Invalid username or password";
        setErrors({ form: errorMsg });
        
        // Shake animation for error
        const form = document.querySelector('.login-form');
        form?.classList.add('animate-shake');
        setTimeout(() => {
          form?.classList.remove('animate-shake');
        }, 500);
      } finally {
        setIsLoading(false);
      }
    } else {
      // Shake animation for validation errors
      const form = document.querySelector('.login-form');
      form?.classList.add('animate-shake');
      setTimeout(() => {
        form?.classList.remove('animate-shake');
      }, 500);
    }
  };

  // Create error message component for consistent styling
  const ErrorMessage = ({ message }: { message: string }) => (
    <div className="error-message text-red-100 bg-red-500 bg-opacity-50 p-2 rounded-md mt-1 animate-fade-in">
      <p>{message}</p>
    </div>
  )

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 transition-all duration-500" style={{ backgroundColor: "#ff7b7b" }}>
      <div className="login-container w-full max-w-md bg-transparent p-8 opacity-0 transition-all duration-700 transform translate-y-4" style={{ animationDuration: '0.7s' }}>
        <h1 className="text-white text-3xl font-bold mb-6 text-center transition-all duration-300 hover:text-red-100">Login</h1>

        {errors.form && <ErrorMessage message={errors.form} />}

        <form onSubmit={handleSubmit} className={`login-form space-y-4 transition-all duration-300 ${loginSuccess ? 'scale-105 opacity-0' : ''}`}>
          <div className="form-group">
            <label className="block text-white mb-2 transition-all duration-300 hover:translate-x-1">Username</label>
            <input
              type="text"
              name="username"
              placeholder="Enter your username"
              className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-2 border-transparent focus:border-red-400 text-gray-800 transition-all duration-300 focus:shadow-lg focus:outline-none transform hover:scale-101"
              value={formData.username}
              onChange={handleChange}
            />
            {errors.username && <ErrorMessage message={errors.username} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2 transition-all duration-300 hover:translate-x-1">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="••••••••"
                className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-2 border-transparent focus:border-red-400 pr-10 text-gray-800 transition-all duration-300 focus:shadow-lg focus:outline-none transform hover:scale-101"
                value={formData.password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-700 hover:text-red-500 transition-colors duration-300"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 transform hover:scale-110 transition-transform duration-300" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 transform hover:scale-110 transition-transform duration-300" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                    <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                  </svg>
                )}
              </button>
            </div>
            {errors.password && <ErrorMessage message={errors.password} />}
          </div>

          <button 
            type="submit" 
            className={`login-button w-full py-3 px-4 bg-red-500 hover:bg-red-600 text-white border-none rounded-3xl text-lg mt-5 transition-all duration-300 transform hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-red-300 active:scale-95 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Logging in...
              </div>
            ) : loginSuccess ? (
              <div className="flex items-center justify-center">
                <svg className="w-6 h-6 mr-2 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Success!
              </div>
            ) : (
              "Log In"
            )}
          </button>

          <div className="text-center text-white mt-5 signup-link">
            <p>
              Don't Have An Account? <a href="/signup" className="text-blue-300 hover:text-blue-100 hover:underline transition-all duration-300 transform inline-block hover:translate-x-1">Sign Up Here</a>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginPage