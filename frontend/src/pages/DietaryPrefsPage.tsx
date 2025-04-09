"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import { recommendations } from "../services/api"

interface DietaryPreference {
  id: string;
  name: string;
  isSelected: boolean;
}

const DietaryPrefsPage = () => {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [preferences, setPreferences] = useState<DietaryPreference[]>([])
  
  useEffect(() => {
    // Only redirect if we're done loading and not authenticated
    if (!isLoading && !isAuthenticated) {
      navigate("/login")
      return
    }
  }, [isAuthenticated, navigate, isLoading])

  // Fetch dietary preferences when component loads
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const fetchPreferences = async () => {
      try {
        const response = await recommendations.getDietaryPreferences();
        setPreferences(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dietary preferences:", error);
        setLoading(false);
      }
    };

    fetchPreferences();
  }, [isAuthenticated]);

  const togglePreference = (id: string) => {
    setPreferences(prev => 
      prev.map(pref => 
        pref.id === id ? { ...pref, isSelected: !pref.isSelected } : pref
      )
    );
  }

  const handleSave = async () => {
    try {
      setSaving(true);
      // Get IDs of selected preferences
      const selectedPreferences = preferences
        .filter(pref => pref.isSelected)
        .map(pref => pref.id);
      
      await recommendations.updateDietaryPreferences(selectedPreferences);
      
      // Explicitly refresh recommendations to get AI updates right away
      await recommendations.refreshRecommendations();
      
      // Navigate back
      navigate("/home");
    } catch (error) {
      console.error("Error saving dietary preferences:", error);
      setSaving(false);
    }
  }

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-red-400 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg text-white"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1"></div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Dietary Preferences</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      <div className="mb-6">
        <p className="text-white/80 text-sm text-center">
          Select your dietary preferences to help us recommend suitable recipes for you.
        </p>
      </div>

      <div className="bg-white rounded-lg p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {preferences.map((preference) => (
            <label key={preference.id} className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                className="checkbox checkbox-primary"
                checked={preference.isSelected}
                onChange={() => togglePreference(preference.id)}
                disabled={saving}
              />
              <span className="text-gray-700">{preference.name}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex justify-center">
        <button 
          className={`btn bg-red-500 hover:bg-red-600 text-white border-none px-8 ${saving ? 'loading' : ''}`} 
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  )
}

export default DietaryPrefsPage