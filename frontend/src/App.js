// App.js
import React, { useState } from 'react';
import { Globe, Users } from 'lucide-react';
import './index.css';
import WorkflowEditor from './components/WorkflowEditor';
import ProfileManager from './components/ProfileManager';

const App = () => {
  const [activeTab, setActiveTab] = useState('workflow');

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-full mx-auto px-4">
          <div className="flex h-16 justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-800">Workflow Automation</h1>
              <div className="ml-6 flex space-x-4">
                <button
                  onClick={() => setActiveTab('workflow')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'workflow' 
                      ? 'bg-gray-100 text-gray-900' 
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  <Globe className="w-5 h-5 inline-block mr-1" />
                  Workflow
                </button>
                <button
                  onClick={() => setActiveTab('profiles')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'profiles' 
                      ? 'bg-gray-100 text-gray-900' 
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  <Users className="w-5 h-5 inline-block mr-1" />
                  Profiles
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
                Save
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        {activeTab === 'workflow' ? <WorkflowEditor /> : <ProfileManager />}
      </main>
    </div>
  );
};

export default App;