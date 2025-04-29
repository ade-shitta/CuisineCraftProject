import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { auth } from '../services/api';

interface ProfileEditModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProfileEditModal: React.FC<ProfileEditModalProps> = ({ isOpen, onClose }) => {
  const { user, updateUser } = useAuth();
  const [firstName, setFirstName] = useState(user?.firstName || '');
  const [lastName, setLastName] = useState(user?.lastName || '');
  const [username, setUsername] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(user?.profileImage || null);
  const [isHovering, setIsHovering] = useState(false);

  // Reset form when modal opens with latest user data
  useEffect(() => {
    if (isOpen && user) {
      setFirstName(user.firstName || '');
      setLastName(user.lastName || '');
      setUsername(user.username || '');
      setEmail(user.email || '');
      setPreviewUrl(user.profileImage || null);
      setSelectedFile(null);
      setError('');
    }
  }, [isOpen, user]);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      
      // Create a preview URL
      const fileReader = new FileReader();
      fileReader.onload = () => {
        setPreviewUrl(fileReader.result as string);
      };
      fileReader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      
      // Use the exact field names the backend expects
      formData.append('username', username);
      formData.append('email', email);
      formData.append('firstName', firstName);
      formData.append('lastName', lastName);
      
      if (selectedFile) {
        formData.append('profileImage', selectedFile);
      }

      const updateResponse = await auth.updateProfile(formData);
      console.log('Profile update response:', updateResponse);

      if (user) {
        const response = await auth.getProfile();
        
        updateUser({
          id: response.data.id,
          username: response.data.username,
          firstName: response.data.firstName,
          lastName: response.data.lastName,
          email: response.data.email,
          dateOfBirth: response.data.dateOfBirth,
          profileImage: response.data.profileImage,
        });
        
        onClose();
      }
    } catch (err: any) {
      console.error('Profile update error:', err);
      
      if (err.response) {
        setError(`Error ${err.response.status}: ${err.response.data?.message || err.response.data?.detail || 'Failed to update profile'}`);
      } else if (err.request) {
        setError('No response received from server. Check your connection.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div 
        className="rounded-lg p-6 w-full max-w-md"
        style={{ backgroundColor: "#ff7b7b" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-bold mb-4 text-white">Edit Profile</h2>
        
        {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          {/* Hidden file input */}
          <input 
            id="profilePicture"
            type="file" 
            className="hidden"
            onChange={handleFileChange}
            ref={fileInputRef}
            aria-label="Profile Picture"
            accept="image/*"
          />

          {/* Profile Picture Preview - Now Clickable */}
          <div className="mb-6 flex flex-col items-center">
            <div 
              className="relative w-32 h-32 rounded-full mb-3 overflow-hidden border-4 border-white group cursor-pointer"
              onClick={triggerFileInput}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              role="button"
              aria-label="Change profile picture"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  triggerFileInput();
                }
              }}
            >
              {previewUrl ? (
                <img 
                  src={previewUrl} 
                  alt="Profile Preview" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-white bg-opacity-90 flex items-center justify-center text-gray-500">
                  No Image
                </div>
              )}
              
              {/* Overlay with edit icon/text */}
              <div 
                className={`absolute inset-0 bg-black bg-opacity-60 flex flex-col items-center justify-center text-white transition-opacity ${
                  isHovering ? 'opacity-100' : 'opacity-0'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="text-xs font-semibold">Change Photo</span>
              </div>
            </div>
            
            <p className="text-white text-sm text-center mb-2">
              Click on the image to change your profile picture
            </p>
          </div>
          
          <div className="mb-4">
            <label htmlFor="firstName" className="block text-white mb-1">First Name</label>
            <input 
              id="firstName"
              type="text" 
              className="w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              aria-label="First Name"
              placeholder="Enter your first name"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="lastName" className="block text-white mb-1">Last Name</label>
            <input 
              id="lastName"
              type="text" 
              className="w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              aria-label="Last Name"
              placeholder="Enter your last name"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="username" className="block text-white mb-1">Username</label>
            <input 
              id="username"
              type="text" 
              className="w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              aria-label="Username"
              placeholder="Enter your username"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="email" className="block text-white mb-1">Email</label>
            <input 
              id="email"
              type="email" 
              className="w-full py-3 px-4 rounded-3xl bg-white bg-opacity-90 border-none text-gray-800"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              aria-label="Email"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              className="px-4 py-3 bg-white bg-opacity-25 rounded-3xl hover:bg-opacity-40 text-white font-bold"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-3 bg-red-500 rounded-3xl hover:bg-red-600 text-white font-bold"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileEditModal;