// hooks/useWorkflow.js
import { useState, useCallback } from 'react';
import { api } from '../services/api';

export const useWorkflow = () => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const addNode = useCallback((nodeData) => {
    setNodes(current => [...current, {
      id: `node-${Date.now()}`,
      ...nodeData
    }]);
  }, []);

  const removeNode = useCallback((nodeId) => {
    setNodes(current => current.filter(node => node.id !== nodeId));
    setEdges(current => current.filter(edge =>
      edge.source !== nodeId && edge.target !== nodeId
    ));
  }, []);

  const addEdge = useCallback((edge) => {
    setEdges(current => [...current, {
      id: `edge-${Date.now()}`,
      ...edge
    }]);
  }, []);

  const removeEdge = useCallback((edgeId) => {
    setEdges(current => current.filter(edge => edge.id !== edgeId));
  }, []);

  const updateNodePosition = useCallback((nodeId, position) => {
    setNodes(current => current.map(node =>
      node.id === nodeId
        ? { ...node, position }
        : node
    ));
  }, []);

  const updateNodeData = useCallback((nodeId, data) => {
    setNodes(current => current.map(node =>
      node.id === nodeId
        ? { ...node, data: { ...node.data, ...data } }
        : node
    ));
  }, []);

  const connectNodes = useCallback((sourceId, targetId) => {
    const sourceNode = nodes.find(node => node.id === sourceId);
    const targetNode = nodes.find(node => node.id === targetId);

    if (sourceNode && targetNode) {
      addEdge({
        source: sourceId,
        target: targetId
      });
    }
  }, [nodes, addEdge]);

  const executeWorkflow = async () => {
    try {
      setIsExecuting(true);
      const workflow = { nodes, edges };
      await api.executeWorkflow(workflow);
    } catch (error) {
      console.error('Workflow execution failed:', error);
      throw error;
    } finally {
      setIsExecuting(false);
    }
  };

  const saveWorkflow = async (name) => {
    try {
      const workflow = {
        name,
        nodes,
        edges,
        createdAt: new Date().toISOString()
      };
      await api.saveWorkflow(workflow);
    } catch (error) {
      console.error('Failed to save workflow:', error);
      throw error;
    }
  };

  const loadWorkflow = async (workflowId) => {
    try {
      const workflow = await api.getWorkflow(workflowId);
      setNodes(workflow.nodes);
      setEdges(workflow.edges);
    } catch (error) {
      console.error('Failed to load workflow:', error);
      throw error;
    }
  };

  const clearWorkflow = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
  }, []);

  const validateWorkflow = useCallback(() => {
    // Check if workflow has at least one node
    if (nodes.length === 0) {
      throw new Error('Workflow must have at least one node');
    }

    // Check if workflow has a trigger node
    const hasTrigger = nodes.some(node => node.type === 'trigger');
    if (!hasTrigger) {
      throw new Error('Workflow must have a trigger node');
    }

    // Check if all nodes are connected
    const nodeIds = new Set(nodes.map(node => node.id));
    const connectedNodes = new Set();

    edges.forEach(edge => {
      connectedNodes.add(edge.source);
      connectedNodes.add(edge.target);
    });

    const disconnectedNodes = [...nodeIds].filter(id => !connectedNodes.has(id));
    if (disconnectedNodes.length > 0) {
      throw new Error('All nodes must be connected');
    }

    return true;
  }, [nodes, edges]);

  return {
    nodes,
    edges,
    selectedNode,
    isExecuting,
    addNode,
    removeNode,
    addEdge,
    removeEdge,
    updateNodePosition,
    updateNodeData,
    connectNodes,
    setSelectedNode,
    executeWorkflow,
    saveWorkflow,
    loadWorkflow,
    clearWorkflow,
    validateWorkflow
  };
};