

import type React from "react"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { fetchCSRFToken } from "../services/csrf"

const SignupPage = () => {
  const navigate = useNavigate()
  const { signup } = useAuth()

  const [formData, setFormData] = useState({
    username: "",
    firstName: "",
    lastName: "",
    email: "",
    dateOfBirth: "",
    password: "",
    confirmPassword: "",
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

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
    if (!formData.firstName) newErrors.firstName = "First name is required"
    if (!formData.lastName) newErrors.lastName = "Last name is required"
    if (!formData.email) newErrors.email = "Email is required"
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Email is invalid"
    if (!formData.dateOfBirth) newErrors.dateOfBirth = "Date of birth is required"
    if (!formData.password) newErrors.password = "Password is required"
    else if (formData.password.length < 6) newErrors.password = "Password must be at least 6 characters"
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Passwords do not match"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (validate()) {
      try {
        // Ensure we have a fresh CSRF token
        await fetchCSRFToken()
        
        await signup({
          username: formData.username,
          firstName: formData.firstName,
          lastName: formData.lastName,
          email: formData.email,
          dateOfBirth: formData.dateOfBirth,
          password: formData.password,
        })
        navigate("/dietary-preferences")
      } catch (error) {
        console.error("Signup error:", error)
        setErrors({ form: "Failed to sign up. Please try again." })
      }
    }
  }

  // Create error message component for consistent styling
  const ErrorMessage = ({ message }: { message: string }) => (
    <div className="error-message">
      <p>{message}</p>
    </div>
  )

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4" style={{ backgroundColor: "#ff7b7b" }}>
      <div className="w-full max-w-md bg-transparent p-8">
        <h1 className="text-white text-2xl font-bold mb-6 text-center">Signup</h1>
        
        {errors.form && <ErrorMessage message={errors.form} />}

        <form onSubmit={handleSubmit} className="signup-form space-y-4">
          <div className="form-group">
            <label className="block text-white mb-2">Username</label>
            <input
              type="text"
              name="username"
              placeholder="Enter a username"
              className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={formData.username}
              onChange={handleChange}
            />
            {errors.username && <ErrorMessage message={errors.username} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2">First Name</label>
            <input
              type="text"
              name="firstName"
              placeholder="First Name"
              className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={formData.firstName}
              onChange={handleChange}
            />
            {errors.firstName && <ErrorMessage message={errors.firstName} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2">Last Name</label>
            <input
              type="text"
              name="lastName"
              placeholder="Last Name"
              className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={formData.lastName}
              onChange={handleChange}
            />
            {errors.lastName && <ErrorMessage message={errors.lastName} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2">Email</label>
            <input
              type="email"
              name="email"
              placeholder="example@example.com"
              className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={formData.email}
              onChange={handleChange}
            />
            {errors.email && <ErrorMessage message={errors.email} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2">Date Of Birth (DD/MM/YYYY)</label>
            <input
              type="date"
              name="dateOfBirth"
              placeholder="DD/MM/YYYY"
              className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={formData.dateOfBirth}
              onChange={handleChange}
            />
            {errors.dateOfBirth && <ErrorMessage message={errors.dateOfBirth} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="••••••••"
                className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none pr-10 text-gray-800"
                value={formData.password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-700"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                    <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                  </svg>
                )}
              </button>
            </div>
            {errors.password && <ErrorMessage message={errors.password} />}
          </div>

          <div className="form-group">
            <label className="block text-white mb-2">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                placeholder="••••••••"
                className="form-input w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none pr-10 text-gray-800"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-700"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                    <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                  </svg>
                )}
              </button>
            </div>
            {errors.confirmPassword && <ErrorMessage message={errors.confirmPassword} />}
          </div>

          <button 
            type="submit" 
            className="signup-button w-full py-3 px-4 bg-red-500 hover:bg-red-600 text-white border-none rounded-3xl text-lg mt-5"
          >
            Sign Up
          </button>

          <div className="text-center text-white mt-5 login-link">
            <p>
              Already Have An Account? <a href="/login" className="text-blue-300 hover:underline">Log In Here</a>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SignupPage