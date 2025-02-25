// components/WorkflowEditor/Connection.js
import React, { useState } from 'react';
import ConnectionPoint from './ConnectionPoint';

const Connection = ({
  fromNode,
  toNode,
  isSelected,
  connectionId,
  handleAddNodeToConnection,
  handleDeleteConnection,
  onMouseEnter,
  onMouseLeave
}) => {
  const [isHovered, setIsHovered] = useState(false);

  if (!fromNode || !toNode || !connectionId) return null;

  // Calculate start and end points
  const startX = fromNode.position.x + 192;
  const startY = fromNode.position.y + 32;
  const endX = toNode.position.x;
  const endY = toNode.position.y + 32;

  // Calculate control points for the curve
  const distance = Math.abs(endX - startX);
  const controlPointOffset = Math.min(distance * 0.5, 150);
  const controlPoint1X = startX + controlPointOffset;
  const controlPoint1Y = startY;
  const controlPoint2X = endX - controlPointOffset;
  const controlPoint2Y = endY;

  // Create path for curved line
  const path = `M ${startX} ${startY} 
                C ${controlPoint1X} ${controlPoint1Y},
                  ${controlPoint2X} ${controlPoint2Y},
                  ${endX} ${endY}`;

  // Calculate the actual midpoint on the curve
  const t = 0.5; // Parameter for the midpoint (0 to 1)
  const midX = Math.pow(1-t, 3) * startX +
               3 * Math.pow(1-t, 2) * t * controlPoint1X +
               3 * (1-t) * Math.pow(t, 2) * controlPoint2X +
               Math.pow(t, 3) * endX;

  const midY = Math.pow(1-t, 3) * startY +
               3 * Math.pow(1-t, 2) * t * controlPoint1Y +
               3 * (1-t) * Math.pow(t, 2) * controlPoint2Y +
               Math.pow(t, 3) * endY;

  // Add arrow marker for direction
  const arrowSize = 8;
  const arrowAngle = Math.atan2(endY - startY, endX - startX);
  const arrowX1 = endX - arrowSize * Math.cos(arrowAngle - Math.PI / 6);
  const arrowY1 = endY - arrowSize * Math.sin(arrowAngle - Math.PI / 6);
  const arrowX2 = endX - arrowSize * Math.cos(arrowAngle + Math.PI / 6);
  const arrowY2 = endY - arrowSize * Math.sin(arrowAngle + Math.PI / 6);

  const arrowPath = `M ${endX} ${endY} L ${arrowX1} ${arrowY1} L ${arrowX2} ${arrowY2} Z`;

  const handleMouseEnter = () => {
    setIsHovered(true);
    if (onMouseEnter) onMouseEnter();
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    if (onMouseLeave) onMouseLeave();
  };

  // Calculate bounding box for the connection area
  const boundingBox = {
    left: Math.min(startX, endX) - 20,
    top: Math.min(startY, endY) - 20,
    width: Math.abs(endX - startX) + 40,
    height: Math.abs(endY - startY) + 40
  };

  return (
    <div
      className="absolute"
      style={{
        left: boundingBox.left,
        top: boundingBox.top,
        width: boundingBox.width,
        height: boundingBox.height,
        pointerEvents: 'all'
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <svg
        width="100%"
        height="100%"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          pointerEvents: 'none'
        }}
      >
        {/* Invisible wider path for better hover detection */}
        <path
          d={path}
          stroke="transparent"
          strokeWidth="20"
          fill="none"
          transform={`translate(${-boundingBox.left} ${-boundingBox.top})`}
          style={{ pointerEvents: 'all' }}
        />

        {/* Main connection line */}
        <path
          d={path}
          className={`${
            isSelected || isHovered
              ? 'stroke-blue-500' 
              : 'stroke-gray-300'
          }`}
          fill="none"
          strokeWidth="2"
          transform={`translate(${-boundingBox.left} ${-boundingBox.top})`}
        />

        {/* Arrow marker */}
        <path
          d={arrowPath}
          className={`${
            isSelected || isHovered
              ? 'fill-blue-500' 
              : 'fill-gray-300'
          }`}
          transform={`translate(${-boundingBox.left} ${-boundingBox.top})`}
        />

        {/* Animation effect for selected/hovered state */}
        {(isSelected || isHovered) && (
          <path
            d={path}
            className="stroke-blue-300"
            fill="none"
            strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray="1,6"
            strokeDashoffset="0"
            transform={`translate(${-boundingBox.left} ${-boundingBox.top})`}
            style={{
              animation: 'flowDash 1s linear infinite'
            }}
          />
        )}
      </svg>

      {/* Connection Points Container */}
      <div
        style={{
          position: 'absolute',
          left: midX - boundingBox.left - 20,
          top: midY - boundingBox.top - 12, // Adjusted to be closer to the path
          width: 40,
          height: 24,
          opacity: isHovered ? 1 : 0,
          transition: 'opacity 0.2s',
          pointerEvents: isHovered ? 'all' : 'none'
        }}
      >
        <ConnectionPoint
          position={{ x: midX, y: midY }}
          onAddNode={(pos) => handleAddNodeToConnection(connectionId, pos)}
          onDelete={() => handleDeleteConnection(connectionId)}
        />
      </div>
    </div>
  );
};

export default Connection;