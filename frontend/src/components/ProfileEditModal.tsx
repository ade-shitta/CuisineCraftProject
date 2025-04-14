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
  const [previewUrl, setPreviewUrl] = useState<string | null>(user?.profilePicture || null);

  // Reset form when modal opens with latest user data
  useEffect(() => {
    if (isOpen && user) {
      setFirstName(user.firstName || '');
      setLastName(user.lastName || '');
      setUsername(user.username || '');
      setEmail(user.email || '');
      setPreviewUrl(user.profilePicture || null);
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
      
      // Make sure we're using the correct field name that matches the serializer
      if (selectedFile) {
        formData.append('profileImage', selectedFile);
      }

      // For debugging - log what we're sending
      console.log('Updating profile with data:', {
        username,
        email,
        firstName,
        lastName,
        has_profile_image: !!selectedFile
      });

      // Update the user profile
      const updateResponse = await auth.updateProfile(formData);
      console.log('Profile update response:', updateResponse);

      // Refresh the user data after update
      if (user) {
        // Get updated profile info
        const response = await auth.getProfile();
        console.log('Retrieved updated profile:', response.data);
        console.log('Profile image URL:', response.data.profileImage);
        
        // Update user in context with the new data
        updateUser({
          id: response.data.id,
          username: response.data.username,
          firstName: response.data.firstName,
          lastName: response.data.lastName,
          email: response.data.email,
          dateOfBirth: response.data.dateOfBirth,
          profilePicture: response.data.profileImage,
        });
        
        // Close the modal after successful update
        onClose();
      }
    } catch (err: any) {
      console.error('Profile update error:', err);
      
      // More detailed error information
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response data:', err.response.data);
        console.error('Error response status:', err.response.status);
        console.error('Error response headers:', err.response.headers);
        setError(`Error ${err.response.status}: ${err.response.data?.message || err.response.data?.detail || 'Failed to update profile'}`);
      } else if (err.request) {
        // The request was made but no response was received
        console.error('Error request:', err.request);
        setError('No response received from server. Check your connection.');
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error message:', err.message);
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
        className="bg-white rounded-lg p-6 w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Edit Profile</h2>
        
        {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          {/* Profile Picture Preview */}
          <div className="mb-6 flex flex-col items-center">
            <div className="w-24 h-24 rounded-full mb-3 overflow-hidden border-2 border-gray-300">
              {previewUrl ? (
                <img 
                  src={previewUrl} 
                  alt="Profile Preview" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-500">
                  No Image
                </div>
              )}
            </div>
            
            <label htmlFor="profilePicture" className="block text-gray-700 mb-1">Profile Picture</label>
            <input 
              id="profilePicture"
              type="file" 
              className="w-full p-2 border border-gray-300 rounded"
              onChange={handleFileChange}
              ref={fileInputRef}
              aria-label="Profile Picture"
              accept="image/*"
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="firstName" className="block text-gray-700 mb-1">First Name</label>
            <input 
              id="firstName"
              type="text" 
              className="w-full p-2 border border-gray-300 rounded"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              aria-label="First Name"
              placeholder="Enter your first name"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="lastName" className="block text-gray-700 mb-1">Last Name</label>
            <input 
              id="lastName"
              type="text" 
              className="w-full p-2 border border-gray-300 rounded"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              aria-label="Last Name"
              placeholder="Enter your last name"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="username" className="block text-gray-700 mb-1">Username</label>
            <input 
              id="username"
              type="text" 
              className="w-full p-2 border border-gray-300 rounded"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              aria-label="Username"
              placeholder="Enter your username"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-700 mb-1">Email</label>
            <input 
              id="email"
              type="email" 
              className="w-full p-2 border border-gray-300 rounded"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              aria-label="Email"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400 text-gray-800"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-500 rounded hover:bg-red-600 text-white"
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