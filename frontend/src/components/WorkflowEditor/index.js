// components/WorkflowEditor/index.js
import React, { useState } from 'react';
import { Search, Bot, Globe, ArrowLeft, AppWindow, X } from 'lucide-react'; // Changed Apps to AppWindow
import Node from './Node';
import Connection from './Connection';
import WorkflowSuggestion from './WorkflowSuggestion';

const WorkflowEditor = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [nodes, setNodes] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [connections, setConnections] = useState([]);
  const [pendingConnection, setPendingConnection] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [connectionPoints, setConnectionPoints] = useState({});  // Store midpoints for each connection
  const [showNodeDialog, setShowNodeDialog] = useState(false);
  const [pendingNodePosition, setPendingNodePosition] = useState(null);
  const [pendingConnectionId, setPendingConnectionId] = useState(null);
  const [hoveredConnection, setHoveredConnection] = useState(null);

  const categories = [
    {
      id: 'ai',
      title: 'Advanced AI',
      description: 'Build autonomous agents, summarize or search documents, etc.',
      icon: Bot,
      nodes: [
        {
          id: 'ai-agent',
          title: 'AI Agent',
          description: 'Generates an action plan and executes it. Can use external tools.',
          icon: Bot
        },
        {
          id: 'openai',
          title: 'OpenAI',
          description: 'Message an assistant or GPT, analyze images, generate audio, etc.',
          icon: Bot
        }
      ]
    },
    {
      id: 'browser',
      title: 'Action in browser',
      description: 'Control browser actions like navigation, clicks, and form filling',
      icon: Globe,
      nodes: [
        {
          id: 'navigate',
          title: 'Navigate',
          description: 'Go to a specific URL',
          icon: Globe
        },
        {
          id: 'click',
          title: 'Click Element',
          description: 'Click on a specific element in the page',
          icon: Globe
        }
      ]
    },
    {
      id: 'app',
      title: 'Action in app',
      description: 'Do something in an app or service like Google Sheets, Telegram or Notion',
      icon: AppWindow,
      nodes: [
        {
          id: 'google-sheets',
          title: 'Google Sheets',
          description: 'Read or write data in Google Sheets',
          icon: AppWindow
        },
        {
          id: 'telegram',
          title: 'Telegram',
          description: 'Send or receive messages in Telegram',
          icon: AppWindow
        }
      ]
    }
  ];

  const [addingNodeToConnection, setAddingNodeToConnection] = useState({
    isAdding: false,
    connectionId: null,
    position: null
  });

  const handleAddNode = (nodeType) => {
    if (addingNodeToConnection.isAdding) {
      // Find the connection
      const connection = connections.find(c => c.id === addingNodeToConnection.connectionId);
      if (!connection) return;
  
      // Create new node
      const newNode = {
        id: `node-${Date.now()}`,
        type: nodeType.id,
        title: nodeType.title,
        position: {
          x: addingNodeToConnection.position.x - 96,
          y: addingNodeToConnection.position.y - 32
        },
        icon: nodeType.icon
      };
  
      // Create two new connections
      const newConnections = [
        {
          id: `${connection.source}-${newNode.id}`,
          source: connection.source,
          target: newNode.id
        },
        {
          id: `${newNode.id}-${connection.target}`,
          source: newNode.id,
          target: connection.target
        }
      ];
  
      // Update state
      setNodes([...nodes, newNode]);
      setConnections([
        ...connections.filter(c => c.id !== addingNodeToConnection.connectionId),
        ...newConnections
      ]);
  
      // Reset states
      setAddingNodeToConnection({
        isAdding: false,
        connectionId: null,
        position: null
      });
      setSelectedCategory(null);
    } else {
      // Original add node logic
      const newNode = {
        id: `node-${Date.now()}`,
        type: nodeType.id,
        title: nodeType.title,
        position: { x: 100, y: 100 },
        icon: nodeType.icon
      };
  
      setNodes([...nodes, newNode]);
    }
  };

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const handleStartConnection = (sourceNodeId) => {
    setPendingConnection({ sourceNodeId });
  };

  const handleEndConnection = (targetNodeId) => {
    if (pendingConnection && pendingConnection.sourceNodeId !== targetNodeId) {
      const newConnectionId = `connection-${Date.now()}`; // Create a unique ID
      setConnections([
        ...connections,
        {
          id: newConnectionId,  // Use the unique ID instead of source-target combination
          source: pendingConnection.sourceNodeId,
          target: targetNodeId,
          createdAt: Date.now() // Add timestamp for better tracking
        }
      ]);
    }
    setPendingConnection(null);
  };

  const calculateConnectionPoints = (sourceNode, targetNode) => {
    const NODE_WIDTH = 192;
    const NODE_HEIGHT = 64;
    const PORT_SIZE = 12; // Size of the connection port circle
    
  // Calculate exact port positions
  const sourceX = sourceNode.position.x + NODE_WIDTH;  // Right edge
  const sourceY = sourceNode.position.y + (NODE_HEIGHT / 2);  // Vertical center
  const targetX = targetNode.position.x;  // Left edge
  const targetY = targetNode.position.y + (NODE_HEIGHT / 2);  // Vertical center
    
    // Calculate midpoint with slight vertical offset for curve
    const midX = (sourceX + targetX) / 2;
    const midY = (sourceY + targetY) / 2;
    
  // Calculate curve control points
  const distance = Math.abs(targetX - sourceX);
  const controlOffset = Math.min(distance * 0.5, 150); // Cap the maximum curve
    
    
    return {
      sourceX,
      sourceY,
      targetX,
      targetY,
      midX,
      midY,
      controlPoint1X: sourceX + controlOffset,
      controlPoint1Y: sourceY,
      controlPoint2X: targetX - controlOffset,
      controlPoint2Y: targetY
    };
  };

  const calculatePath = (points) => {
    const {
      sourceX, sourceY,
      targetX, targetY,
      controlPoint1X, controlPoint1Y,
      controlPoint2X, controlPoint2Y
    } = points;

    return `M ${sourceX} ${sourceY} 
            C ${controlPoint1X} ${controlPoint1Y},
              ${controlPoint2X} ${controlPoint2Y},
              ${targetX} ${targetY}`;
  };

  const handleAddNodeToConnection = (connectionId, position) => {
    setAddingNodeToConnection({
      isAdding: true,
      connectionId,
      position
    });
    setSelectedCategory('ai'); // or whichever category you want to show first
  };
  
  

const handleNodeSelection = (nodeType) => {
  if (pendingConnectionId && pendingNodePosition) {
    // Find the connection
    const connection = connections.find(c => c.id === pendingConnectionId);
    if (!connection) return;

    // Create new node
    const newNode = {
      id: `node-${Date.now()}`,
      type: nodeType.id,
      title: nodeType.title,
      icon: nodeType.icon,
      position: {
        x: pendingNodePosition.x - 96,
        y: pendingNodePosition.y - 32
      }
    };

    // Create two new connections
// Create two new connections
const newConnections = [
  {
    id: `connection-${Date.now()}-1`, // Unique timestamp-based ID with suffix
    source: connection.source,
    target: newNode.id
  },
  {
    id: `connection-${Date.now()}-2`, // Different suffix ensures uniqueness
    source: newNode.id,
    target: connection.target
  }
];

    // Update state
    setNodes([...nodes, newNode]);
    setConnections([
      ...connections.filter(c => c.id !== pendingConnectionId),
      ...newConnections
    ]);

    // Reset pending states
    setPendingConnectionId(null);
    setPendingNodePosition(null);
    setShowNodeDialog(false);
  }
};

const handleDeleteConnection = (connectionId) => {
    console.log('Before delete - connections:', connections);
    console.log('Deleting connection with ID:', connectionId);
    
    setConnections(prevConnections => {
      const updatedConnections = prevConnections.filter(c => c.id !== connectionId);
      console.log('After delete - connections:', updatedConnections);
      return updatedConnections;
    });
  };

  const renderConnections = () => {
    return (
      <div className="absolute inset-0">
        {connections.map(connection => {
          const sourceNode = nodes.find(n => n.id === connection.source);
          const targetNode = nodes.find(n => n.id === connection.target);
          if (!sourceNode || !targetNode) return null;
  
          const points = calculateConnectionPoints(sourceNode, targetNode);
          const path = calculatePath(points);
  
          return (
            <Connection
              key={connection.id}
              fromNode={sourceNode}
              toNode={targetNode}
              isSelected={selectedNode === connection.id}
              connectionId={connection.id}
              points={points}  // Pass the calculated points
              path={path}     // Pass the calculated path
              handleAddNodeToConnection={handleAddNodeToConnection}
              handleDeleteConnection={handleDeleteConnection}
              // Add these props for better control
              onMouseEnter={() => setHoveredConnection(connection.id)}
              onMouseLeave={() => setHoveredConnection(null)}
            />
          );
        })}
  
        {/* Pending connection line */}
        {pendingConnection && (
          <svg className="absolute inset-0 pointer-events-none">
            <path
              d={calculatePath({
                sourceX: nodes.find(n => n.id === pendingConnection.sourceNodeId).position.x + 192 + 6,
                sourceY: nodes.find(n => n.id === pendingConnection.sourceNodeId).position.y + 32,
                targetX: mousePosition.x,
                targetY: mousePosition.y,
                controlPoint1X: nodes.find(n => n.id === pendingConnection.sourceNodeId).position.x + 242,
                controlPoint1Y: nodes.find(n => n.id === pendingConnection.sourceNodeId).position.y + 32,
                controlPoint2X: mousePosition.x - 50,
                controlPoint2Y: mousePosition.y
              })}
              stroke="#94a3b8"
              strokeWidth="2"
              strokeDasharray="5,5"
              fill="none"
            />
          </svg>
        )}
      </div>
    );
  };

  const renderNodeConfig = (node) => {
    // Configuration panels for different node types
    const configs = {
      'navigate': (
        <div>
          <h3 className="text-lg font-medium mb-4">Navigate Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={node.config?.url || ''}
                onChange={(e) => updateNodeConfig(node.id, { url: e.target.value })}
                placeholder="https://example.com"
              />
            </div>
          </div>
        </div>
      ),
      'openai': (
        <div>
          <h3 className="text-lg font-medium mb-4">OpenAI Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prompt</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={node.config?.prompt || ''}
                onChange={(e) => updateNodeConfig(node.id, { prompt: e.target.value })}
                rows={4}
                placeholder="Enter your prompt here..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={node.config?.model || 'gpt-4'}
                onChange={(e) => updateNodeConfig(node.id, { model: e.target.value })}
              >
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </select>
            </div>
          </div>
        </div>
      ),
      // Add more configuration panels for other node types as needed
    };

    return configs[node.type] || (
      <div className="text-gray-500">No configuration available for this node type.</div>
    );
  };

  const updateNodeConfig = (nodeId, newConfig) => {
    setNodes(nodes.map(node =>
      node.id === nodeId
        ? { ...node, config: { ...node.config, ...newConfig } }
        : node
    ));
  };

  const renderSidebar = () => {
    if (selectedNode) {
      const node = nodes.find(n => n.id === selectedNode);
      return (
        <>
          <div className="flex items-center mb-6">
            <button
              onClick={() => setSelectedNode(null)}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </button>
          </div>
          {renderNodeConfig(node)}
        </>
      );
    }

    if (selectedCategory) {
      // Show nodes for selected category
      const category = categories.find(c => c.id === selectedCategory);
      return (
        <>
          <div className="flex items-center mb-6">
            <button
              onClick={() => setSelectedCategory(null)}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </button>
          </div>
          <h2 className="text-xl font-semibold mb-2">{category.title}</h2>
          <p className="text-gray-500 mb-4">{category.description}</p>
          <div className="space-y-4">
            {category.nodes.map(node => (
              <div
                key={node.id}
                className="flex items-start p-4 hover:bg-gray-50 rounded-lg cursor-pointer"
                onClick={() => handleAddNode(node)}
              >
                <div className="flex-shrink-0 p-2 bg-gray-100 rounded-lg">
                  <node.icon className="w-5 h-5 text-gray-600" />
                </div>
                <div className="ml-4">
                  <h3 className="font-medium">{node.title}</h3>
                  <p className="text-sm text-gray-500">{node.description}</p>
                </div>
              </div>
            ))}
          </div>
        </>
      );
    }

    // Show main categories
    return (
      <>
        <h2 className="text-xl font-semibold mb-2">Add a node</h2>
        <p className="text-gray-500 mb-4">Select a category to add a node to your workflow</p>
        <div className="space-y-4">
          {categories.map(category => (
            <div
              key={category.id}
              className="flex items-start p-4 hover:bg-gray-50 rounded-lg cursor-pointer"
              onClick={() => setSelectedCategory(category.id)}
            >
              <div className="flex-shrink-0 p-2 bg-gray-100 rounded-lg">
                <category.icon className="w-5 h-5 text-gray-600" />
              </div>
              <div className="ml-4">
                <h3 className="font-medium">{category.title}</h3>
                <p className="text-sm text-gray-500">{category.description}</p>
              </div>
            </div>
          ))}
        </div>
      </>
    );
  };

  const handleWorkflowSuggestion = (workflow) => {
    // Assuming workflow is an object with nodes and connections
    const offsetX = 100; // Starting X position for the workflow
    const offsetY = 100; // Starting Y position for the workflow

    // Add position information to the nodes
    const positionedNodes = workflow.nodes.map((node, index) => ({
      ...node,
      id: `node-${Date.now()}-${index}`, // Ensure unique IDs
      position: {
        x: offsetX + (index * 250), // Space nodes horizontally
        y: offsetY
      }
    }));

    // Update the connections with the new node IDs
    const updatedConnections = workflow.connections.map((connection, index) => ({
      id: `connection-${Date.now()}-${index}`,
      source: positionedNodes[connection.sourceIndex].id,
      target: positionedNodes[connection.targetIndex].id
    }));

    // Update state
    setNodes([...nodes, ...positionedNodes]);
    setConnections([...connections, ...updatedConnections]);
  };

  return (
    <div className="flex flex-col h-screen">
      <WorkflowSuggestion onSuggest={handleWorkflowSuggestion} />
      <div className="flex flex-1">
        {/* Main workflow area */}
        <div 
          className="flex-1 relative bg-gray-50"
          onMouseMove={handleMouseMove}
        >
          {nodes.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 mx-auto">
                  <div className="text-2xl text-gray-400">Add first step...</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="relative w-full h-full">
              {renderConnections()}
              {nodes.map((node) => (
                <Node
                  key={node.id}
                  data={node}
                  isSelected={node.id === selectedNode}
                  onSelect={() => setSelectedNode(node.id)}
                  onPositionChange={(nodeId, newPosition) => {
                    setNodes(nodes.map(n =>
                      n.id === nodeId ? { ...n, position: newPosition } : n
                    ));
                  }}
                  onStartConnection={handleStartConnection}
                  onEndConnection={handleEndConnection}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right sidebar */}
        <div className="w-96 bg-white border-l border-gray-200 p-6 overflow-y-auto">
          {renderSidebar()}
        </div>

      </div>
    </div>
  );
};

export default WorkflowEditor;