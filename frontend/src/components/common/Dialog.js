// components/common/Dialog.js
import React from 'react';
import { X } from 'lucide-react';

const Dialog = ({
  isOpen,
  onClose,
  title,
  children
}) => {
  if (!isOpen) return null;

  const handleDialogClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md"
        onClick={handleDialogClick}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="mb-4">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Dialog;