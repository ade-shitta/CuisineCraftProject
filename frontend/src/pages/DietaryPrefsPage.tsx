

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import { recommendations } from "../services/api"
import AllergyItem from "../components/AllergyItem"

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
    if (!isLoading && !isAuthenticated) {
      navigate("/login")
      return
    }
  }, [isAuthenticated, navigate, isLoading])

  useEffect(() => {
    if (!isAuthenticated) return;
    
    const fetchPreferences = async () => {
      try {
        const response = await recommendations.getDietaryPreferences();
        setPreferences(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch dietary preferences", error);
        setLoading(false);
      }
    };
    
    fetchPreferences();
  }, [isAuthenticated]);

  const togglePreference = (id: string) => {
    setPreferences(preferences.map(pref => 
      pref.id === id ? { ...pref, isSelected: !pref.isSelected } : pref
    ));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const selectedPreferences = preferences
        .filter(pref => pref.isSelected)
        .map(pref => pref.id);
      
      await recommendations.updateDietaryPreferences(selectedPreferences);
      setSaving(false);
      navigate('/recipes');
    } catch (error) {
      console.error("Failed to save preferences", error);
      setSaving(false);
    }
  };

  // Handle image errors by showing a fallback
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.src = "/images/dietary/placeholder.png";
  };

  if (loading || isLoading) {
    return (
      <div className="min-h-screen bg-red-400 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg text-white"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1">
          <button
            onClick={() => navigate(-1)}
            className="bg-red-500 hover:bg-red-600 text-white rounded-full w-10 h-10 flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-300 hover:scale-110"
            aria-label="Go back"
            title="Go back"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Dietary Preferences</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      <div className="container mx-auto">
        <div className="max-w-3xl mx-auto">
          {/* Description */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 mb-6 text-center">
            <p className="text-white">
              Select your dietary preferences to help us recommend suitable recipes for you.
            </p>
          </div>

          {/* Preferences card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
            <div className="p-6">
              <h2 className="font-semibold text-gray-800 mb-5 text-xl border-b-2 border-red-400 pb-2">
                Select Your Preferences
              </h2>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {preferences.map((preference) => (
                  <AllergyItem
                    key={preference.id}
                    name={preference.name}
                    image={`/images/dietary/${preference.id}.png`}
                    isSelected={preference.isSelected}
                    onToggle={() => togglePreference(preference.id)}
                    onError={handleImageError}
                  />
                ))}
              </div>
            </div>

            {/* Footer with save button */}
            <div className="bg-gray-50 border-t border-gray-100 p-4 flex justify-end">
              <button 
                className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-md shadow-md"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Preferences'}
              </button>
            </div>
          </div>

          {/* Information card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 mb-6 text-center">
            <p className="text-white text-sm">
              Your preferences help us filter recipes that match your dietary needs.
              You can update these preferences anytime.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DietaryPrefsPage