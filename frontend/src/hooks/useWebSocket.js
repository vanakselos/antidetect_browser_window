// hooks/useWebSocket.js
import { useState, useEffect } from 'react';

export const useWebSocket = () => {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('disconnected');
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');

    websocket.onopen = () => {
      setStatus('connected');
      console.log('WebSocket Connected');
    };

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        setMessages((prevMessages) => [...prevMessages, message]);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('error');
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setStatus('disconnected');
      // Try to reconnect after 5 seconds
      setTimeout(() => {
        setWs(new WebSocket('ws://localhost:8000/ws'));
      }, 5000);
    };

    setWs(websocket);

    // Cleanup on unmount
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const sendMessage = (message) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    messages,
    status,
    sendMessage,
    clearMessages
  };
};