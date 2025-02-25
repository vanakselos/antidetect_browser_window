// components/WorkflowEditor/Toolbar.js
import React from 'react';
import { Plus, Play, Save, Trash2, Settings, Undo, Redo } from 'lucide-react';

const Toolbar = ({
  onAddNode,
  onSave,
  onRun,
  onClear,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  isExecuting,
  selectedProfile
}) => {
  const handleAddNode = (e) => {
    e.preventDefault();
    if (onAddNode) {
      onAddNode();
    }
    console.log("Add Node clicked"); // Debug log
  };

  return (
    <div className="fixed top-20 left-4 bg-white rounded-lg shadow-lg p-2 flex flex-col gap-2">
      <button
        onClick={handleAddNode}
        className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900 transition-colors"
        title="Add Node"
      >
        <Plus className="w-6 h-6" />
      </button>

      <button
        onClick={onSave}
        className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900 transition-colors"
        title="Save Workflow"
      >
        <Save className="w-6 h-6" />
      </button>

      <button
        onClick={onRun}
        disabled={isExecuting}
        className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900 transition-colors"
        title="Run Workflow"
      >
        <Play className="w-6 h-6" />
      </button>

      <button
        onClick={onClear}
        className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900 transition-colors"
        title="Clear Workflow"
      >
        <Trash2 className="w-6 h-6" />
      </button>

      <button
        onClick={() => {/* Handle settings */}}
        className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900 transition-colors"
        title="Workflow Settings"
      >
        <Settings className="w-6 h-6" />
      </button>

      <button
        onClick={onUndo}
        disabled={!canUndo}
        className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors
          ${canUndo 
            ? 'hover:bg-gray-100 text-gray-600 hover:text-gray-900' 
            : 'text-gray-300 cursor-not-allowed'}`}
        title="Undo"
      >
        <Undo className="w-6 h-6" />
      </button>

      <button
        onClick={onRedo}
        disabled={!canRedo}
        className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors
          ${canRedo 
            ? 'hover:bg-gray-100 text-gray-600 hover:text-gray-900' 
            : 'text-gray-300 cursor-not-allowed'}`}
        title="Redo"
      >
        <Redo className="w-6 h-6" />
      </button>
    </div>
  );
};

export default Toolbar;