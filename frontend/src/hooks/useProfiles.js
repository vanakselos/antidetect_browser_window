// hooks/useProfiles.js
import { useState, useEffect } from 'react';
import { api } from '../services/api';

export const useProfiles = () => {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const data = await api.getProfiles();
      setProfiles(data.profiles);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createProfile = async (name) => {
    try {
      await api.createProfile(name);
      await fetchProfiles();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  return {
    profiles,
    loading,
    error,
    createProfile,
    refreshProfiles: fetchProfiles
  };
};

