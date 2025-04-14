"use client"

import React, { createContext, useState, useContext, useEffect } from "react";
import { auth } from "../services/api";
import { fetchCSRFToken } from "../services/csrf";

type User = {
  id: string;
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  dateOfBirth?: string;
  profilePicture?: string;
};

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean; // Add loading state
  login: (username: string, password: string) => Promise<void>;
  signup: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: User) => void; // Add method to update user data
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Add local storage helpers for better persistence
const saveUserToStorage = (user: User | null) => {
  if (user) {
    localStorage.setItem('user', JSON.stringify(user));
  } else {
    localStorage.removeItem('user');
  }
};

const getUserFromStorage = (): User | null => {
  const storedUser = localStorage.getItem('user');
  return storedUser ? JSON.parse(storedUser) : null;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize from localStorage for immediate state reflection
  const [user, setUser] = useState<User | null>(getUserFromStorage());
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!getUserFromStorage());
  const [isLoading, setIsLoading] = useState<boolean>(true); // Add loading state

  // Custom setter for user that also updates localStorage
  const setUserAndStorage = (newUser: User | null) => {
    setUser(newUser);
    saveUserToStorage(newUser);
    setIsAuthenticated(!!newUser);
  };

  useEffect(() => {
    // Check if user is already logged in
    const checkAuthStatus = async () => {
      try {
        // First ensure we have a valid CSRF token
        await fetchCSRFToken();
        
        // Then check if the user is authenticated
        const response = await auth.getProfile();
        
        // Transform snake_case from Django to camelCase for React
        setUserAndStorage({
          id: response.data.id,
          username: response.data.username,
          firstName: response.data.firstName, // Using camelCase from API
          lastName: response.data.lastName,   // Using camelCase from API
          email: response.data.email,
          dateOfBirth: response.data.dateOfBirth,
          profilePicture: response.data.profileImage, // Match the name in the serializer
        });
      } catch (error) {
        console.log("User not authenticated");
        setUserAndStorage(null);
      } finally {
        setIsLoading(false); // Always set loading to false when done
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      // First ensure CSRF token is fresh
      await fetchCSRFToken();
      
      const response = await auth.login(username, password);
      // Transform snake_case from Django to camelCase for React
      setUserAndStorage({
        id: response.data.id,
        username: response.data.username,
        firstName: response.data.firstName, 
        lastName: response.data.lastName,   
        email: response.data.email,
        dateOfBirth: response.data.dateOfBirth,
        profilePicture: response.data.profileImage,
      });
    } catch (error) {
      throw error;
    }
  };

  const signup = async (userData: any) => {
    try {
      await fetchCSRFToken();
      const response = await auth.register(userData);
      setUserAndStorage(response.data);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await auth.logout();
      setUserAndStorage(null);
    } catch (error) {
      // Even if logout API fails, clear local state
      setUserAndStorage(null);
      throw error;
    }
  };

  const updateUser = (userData: User) => {
    setUserAndStorage(userData);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, signup, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};