// services/api.js
const API_URL = 'http://localhost:8000/api';

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }
  return response.json();
};

export const api = {
  // Profile management
  async getProfiles() {
    const response = await fetch(`${API_URL}/profiles`);
    return handleResponse(response);
  },

  async createProfile(name) {
    const response = await fetch(`${API_URL}/profiles`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    });
    return handleResponse(response);
  },

  async deleteProfile(profileName) {
    const response = await fetch(`${API_URL}/profiles/${profileName}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  // Browser control
  async launchBrowser(profileName) {
    const response = await fetch(`${API_URL}/browser/launch/${profileName}`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Workflow management
  async executeWorkflow(workflow) {
    const response = await fetch(`${API_URL}/workflows/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(workflow),
    });
    return handleResponse(response);
  },

  async saveWorkflow(workflow) {
    const response = await fetch(`${API_URL}/workflows/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(workflow),
    });
    return handleResponse(response);
  },

  async getWorkflow(workflowId) {
    const response = await fetch(`${API_URL}/workflows/${workflowId}`);
    return handleResponse(response);
  },

  async getNodes() {
    const response = await fetch(`${API_URL}/workflows/nodes`);
    return handleResponse(response);
  },
};