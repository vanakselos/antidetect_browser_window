// utils/constants.js
export const NODE_TYPES = {
  TRIGGER: 'trigger',
  HTTP: 'http',
  CODE: 'code'
};

export const NODE_CONFIGS = {
  [NODE_TYPES.TRIGGER]: {
    title: 'Schedule Trigger',
    inputs: [],
    outputs: ['next'],
    color: 'blue'
  },
  [NODE_TYPES.HTTP]: {
    title: 'HTTP Request',
    inputs: ['trigger'],
    outputs: ['next'],
    color: 'purple'
  },
  [NODE_TYPES.CODE]: {
    title: 'Code',
    inputs: ['input'],
    outputs: ['output'],
    color: 'orange'
  }
};

export const API_ENDPOINTS = {
  PROFILES: '/api/profiles',
  WORKFLOWS: '/api/workflows',
  BROWSER: '/api/browser'
};

// utils/helpers.js
export const generateId = () => `id-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

export const calculateEdgePath = (start, end) => {
  const midX = (start.x + end.x) / 2;
  return `M ${start.x} ${start.y} 
          C ${midX} ${start.y},
            ${midX} ${end.y},
            ${end.x} ${end.y}`;
};

export const snapToGrid = (position, gridSize = 20) => ({
  x: Math.round(position.x / gridSize) * gridSize,
  y: Math.round(position.y / gridSize) * gridSize
});

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const validateConnection = (source, target) => {
  // Don't allow connections to self
  if (source.nodeId === target.nodeId) return false;

  // Don't allow multiple connections to same input
  if (target.connections.length > 0) return false;

  // Don't allow incompatible types
  const sourceNode = NODE_CONFIGS[source.type];
  const targetNode = NODE_CONFIGS[target.type];

  if (!sourceNode || !targetNode) return false;

  return true;
};