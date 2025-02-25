// components/ProfileManager/ProfileCard.js
import React from 'react';
import { Globe, Settings, Play, Trash2 } from 'lucide-react';

export const ProfileCard = ({ profile, onLaunch, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 hover:shadow-xl transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-medium text-gray-900">{profile.name}</h3>
          <p className="text-sm text-gray-500">Created: {new Date(profile.createdAt).toLocaleDateString()}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(profile)}
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
            title="Edit Profile"
          >
            <Settings className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(profile)}
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
            title="Delete Profile"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">
          <Globe className="w-4 h-4 inline-block mr-1" />
          {profile.fingerprint.userAgent}
        </div>
        <div className="flex gap-2 text-sm text-gray-600">
          <span>{profile.fingerprint.platform}</span>
          <span>•</span>
          <span>{profile.fingerprint.language}</span>
        </div>
      </div>

      <button
        onClick={() => onLaunch(profile)}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2"
      >
        <Play className="w-4 h-4" />
        Launch Browser
      </button>
    </div>
  );
};

