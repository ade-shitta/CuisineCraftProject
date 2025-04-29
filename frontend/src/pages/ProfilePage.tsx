import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import Header from "../components/Header"
import ProfileEditModal from "../components/ProfileEditModal"

const ProfilePage = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [imageError, setImageError] = useState(false)

  // Generate initials from the user's name
  const getInitials = () => {
    if (!user) return 'U';
    
    const firstInitial = user.firstName ? user.firstName.charAt(0).toUpperCase() : '';
    const lastInitial = user.lastName ? user.lastName.charAt(0).toUpperCase() : '';
    
    return firstInitial + lastInitial || 'U';
  };

  // Default avatar URL with initials
  const defaultAvatar = `https://ui-avatars.com/api/?name=${getInitials()}&background=FF7070&color=fff&size=256`;

  // Use ui-avatars service with the user's actual initials
  const profilePicture = !imageError && user?.profileImage 
    ? user.profileImage 
    : defaultAvatar;

  // Log for debugging
  useEffect(() => {
    console.log("User profile data:", user);
    console.log("Profile picture URL:", profilePicture);
  }, [user, profilePicture]);

  const handleLogout = () => {
    logout()
    navigate("/")
  }

  const openModal = () => {
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    // Reset image error when modal is closed to try loading the image again
    setImageError(false)
  }

  const handleImageError = () => {
    console.error("Error loading profile image:", user?.profileImage);
    setImageError(true); // Set error state to use the default avatar
  }

  return (
    <div className="min-h-screen bg-red-400 p-4">
      {/* Updated header layout to match HomePage */}
      <div className="flex justify-between items-center mb-8 px-1">
        <div className="flex-1"></div>
        <div className="text-center flex-1">
          <h1 className="text-white text-2xl font-bold">Profile</h1>
        </div>
        <div className="flex-1 flex justify-end pt-1">
          <Header />
        </div>
      </div>

      <div className="flex flex-col items-center justify-center mt-8">
        <div className="avatar mb-4">
          <div className="w-24 rounded-full ring ring-white">
            <img 
              src={profilePicture} 
              alt="Profile" 
              onError={handleImageError}
            />
          </div>
        </div>

        <h1 className="text-white text-xl font-bold mb-8">
          {user ? `${user.firstName} ${user.lastName}` : "Guest User"}
        </h1>

        <div className="w-full max-w-xs space-y-4">
          <button
            className="btn w-full bg-red-300 hover:bg-red-500 text-white border-none"
            onClick={openModal}
          >
            Edit Profile
          </button>

          <button
            className="btn w-full bg-red-300 hover:bg-red-500 text-white border-none"
            onClick={() => navigate("/dietary-preferences")}
          >
            Edit Dietary Preferences
          </button>

          <button className="btn w-full bg-red-500 hover:bg-red-600 text-white border-none mt-8" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      {/* Profile edit modal */}
      <ProfileEditModal isOpen={isModalOpen} onClose={closeModal} />
    </div>
  )
}

export default ProfilePage