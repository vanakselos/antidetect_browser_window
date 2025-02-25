// components/WorkflowEditor/Node.js
import React, { useState } from 'react';
import { Clock, Play, Power, Trash2, Settings, Circle, ArrowRight } from 'lucide-react';

const nodeStyles = {
  manual: {
    border: 'border-blue-500',
    background: 'bg-blue-100',
    icon: 'text-blue-600'
  },
  app: {
    border: 'border-purple-500',
    background: 'bg-purple-100',
    icon: 'text-purple-600'
  },
  schedule: {
    border: 'border-green-500',
    background: 'bg-green-100',
    icon: 'text-green-600'
  },
  default: {
    border: 'border-gray-200',
    background: 'bg-gray-100',
    icon: 'text-gray-600'
  }
};

const Node = ({ data, isSelected, onSelect, onPositionChange, onStartConnection, onEndConnection }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX - data.position.x,
      y: e.clientY - data.position.y
    });
    e.stopPropagation();
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x;
      const newY = e.clientY - dragStart.y;
      onPositionChange(data.id, { x: newX, y: newY });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleOutputPortMouseDown = (e) => {
    e.stopPropagation(); // Prevent node dragging
    onStartConnection(data.id);
  };

  const handleInputPortMouseDown = (e) => {
    e.stopPropagation(); // Prevent node dragging
    onEndConnection(data.id);
  };

  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragStart]);

  if (!data) return null;

  const style = nodeStyles[data.type] || nodeStyles.default;
  const Icon = data.icon || Clock;

  return (
    <div
      onClick={() => onSelect(data.id)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`absolute bg-white rounded-lg shadow-lg cursor-pointer
        ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      style={{
        left: data.position.x,
        top: data.position.y,
        width: '192px',
        transform: isDragging ? 'scale(1.02)' : 'scale(1)',
        transition: isDragging ? 'none' : 'transform 0.2s'
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Top menu - only show when hovered */}
      {isHovered && (
        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-white rounded-md shadow-lg p-1 flex gap-1">
          <button className="p-1 hover:bg-gray-100 rounded" title="Run">
            <Play className="w-4 h-4 text-gray-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded" title="Active">
            <Power className="w-4 h-4 text-gray-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded" title="Settings">
            <Settings className="w-4 h-4 text-gray-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded" title="Delete">
            <Trash2 className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      )}

      {/* Input port with circle icon */}
      <div
        className="absolute flex items-center"
        style={{
          left: '-12px',
          top: '50%',
          transform: 'translateY(-50%)',
        }}
      >
        <div
          className="w-3 h-3 rounded-full bg-gray-300 hover:bg-blue-400 border-2 border-white"
          onMouseDown={handleInputPortMouseDown}
        />
        <Circle className="w-3 h-3 text-gray-400 ml-1" />
      </div>

      {/* Output port with arrow icon */}
      <div
        className="absolute flex items-center"
        style={{
          right: '-12px',
          top: '50%',
          transform: 'translateY(-50%)',
        }}
      >
        <ArrowRight className="w-3 h-3 text-gray-400 mr-1" />
        <div
          className="w-3 h-3 rounded-full bg-gray-300 hover:bg-blue-400 border-2 border-white"
          onMouseDown={handleOutputPortMouseDown}
        />
      </div>

      {/* Node content */}
      <div className="flex items-center p-4 h-16">
        <div className="flex items-center gap-3 w-full">
          <div className={`p-2 rounded-lg ${style.background} flex-shrink-0`}>
            <Icon className={`w-5 h-5 ${style.icon}`} />
          </div>
          <span className="font-medium text-sm truncate">{data.title}</span>
        </div>
      </div>

      {data.subtitle && (
        <div className="px-4 pb-2 text-xs text-gray-500 truncate">
          {data.subtitle}
        </div>
      )}
    </div>
  );
};

export default Node;