import React, { useState } from 'react';
import {
  Plus,
  Loader,
  Globe,
  Settings,
  Play,
  Trash2,
  AlertCircle
} from 'lucide-react';
import CreateProfileDialog from './CreateProfileDialog';
import { useProfiles } from '../../hooks/useProfiles';
import { api } from '../../services/api';

const ProfileCard = ({ profile, onLaunch, onDelete }) => {
  const [isLaunching, setIsLaunching] = useState(false);
  const [error, setError] = useState(null);

  const handleLaunch = async () => {
    try {
      setIsLaunching(true);
      setError(null);
      await onLaunch(profile);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLaunching(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
      {/* Profile Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{profile.name}</h3>
          <p className="text-sm text-gray-500">
            Created: {new Date(profile.createdAt).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onDelete(profile)}
            className="p-2 hover:bg-red-50 rounded-lg text-red-600"
            title="Delete Profile"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Profile Details */}
      <div className="mb-4 space-y-2">
        <div className="flex items-center text-sm text-gray-600">
          <Globe className="w-4 h-4 mr-2" />
          {profile.fingerprint?.userAgent?.split('/')[0] || 'Default Browser'}
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
          <div>Platform: {profile.fingerprint?.platform || 'Unknown'}</div>
          <div>Language: {profile.fingerprint?.language || 'Default'}</div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-2 bg-red-50 text-red-600 rounded-md flex items-center text-sm">
          <AlertCircle className="w-4 h-4 mr-2" />
          {error}
        </div>
      )}

      {/* Launch Button */}
      <button
        onClick={handleLaunch}
        disabled={isLaunching}
        className={`w-full py-2 px-4 rounded-lg flex items-center justify-center gap-2 
          ${isLaunching 
            ? 'bg-gray-100 text-gray-500 cursor-not-allowed' 
            : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
      >
        {isLaunching ? (
          <Loader className="w-4 h-4 animate-spin" />
        ) : (
          <Play className="w-4 h-4" />
        )}
        {isLaunching ? 'Launching...' : 'Launch Browser'}
      </button>
    </div>
  );
};

const EmptyState = ({ onCreateClick }) => (
  <div className="text-center py-12">
    <Globe className="w-12 h-12 mx-auto text-gray-400 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">No Profiles Yet</h3>
    <p className="text-gray-500 mb-4">Create your first browser profile to get started</p>
    <button
      onClick={onCreateClick}
      className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
    >
      <Plus className="w-5 h-5 mr-2" />
      Create Profile
    </button>
  </div>
);

const ProfileManager = () => {
  const { profiles, loading, error, createProfile } = useProfiles();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [deletingProfile, setDeletingProfile] = useState(null);

  const handleCreateProfile = async (name) => {
    try {
      await createProfile(name);
      // You could add a success toast here
    } catch (error) {
      console.error('Failed to create profile:', error);
      // You could add an error toast here
    }
  };

  const handleLaunchProfile = async (profile) => {
    try {
      await api.launchBrowser(profile.name);
    } catch (error) {
      console.error('Failed to launch browser:', error);
      throw error;
    }
  };

  const handleDeleteProfile = async (profile) => {
    if (window.confirm(`Are you sure you want to delete profile "${profile.name}"?`)) {
      try {
        setDeletingProfile(profile.name);
        await api.deleteProfile(profile.name);
        // Refresh profiles list
        window.location.reload();
      } catch (error) {
        console.error('Failed to delete profile:', error);
      } finally {
        setDeletingProfile(null);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 rounded-lg">
        <div className="flex items-center text-red-600 mb-2">
          <AlertCircle className="w-5 h-5 mr-2" />
          <h3 className="font-medium">Error Loading Profiles</h3>
        </div>
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Browser Profiles</h2>
          <p className="text-gray-500">Manage your browser automation profiles</p>
        </div>
        <button
          onClick={() => setIsDialogOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <Plus className="w-5 h-5" />
          Create Profile
        </button>
      </div>

      {/* Profiles Grid */}
      {profiles.length === 0 ? (
        <EmptyState onCreateClick={() => setIsDialogOpen(true)} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {profiles.map((profile) => (
            <ProfileCard
              key={profile.name}
              profile={profile}
              onLaunch={handleLaunchProfile}
              onDelete={handleDeleteProfile}
              isDeleting={deletingProfile === profile.name}
            />
          ))}
        </div>
      )}

      {/* Create Profile Dialog */}
      <CreateProfileDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onCreate={handleCreateProfile}
      />
    </div>
  );
};

export default ProfileManager;