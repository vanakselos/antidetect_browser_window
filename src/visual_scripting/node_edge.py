from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (QPainterPath, QPen, QColor, QPainter,
                        QBrush)
import math


class Edge(QGraphicsPathItem):
    def __init__(self, start_socket, end_socket=None):
        super().__init__()

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.end_pos = None

        # Visual settings
        self.color = QColor("#FFFFFF")
        self.width = 2.0
        self.selected_color = QColor("#00FF00")


        # Setup
        self.setZValue(-1)  # Draw behind nodes
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Add to socket
        if self.start_socket:
            self.start_socket.edges.append(self)
        if self.end_socket:
            self.end_socket.edges.append(self)

        self.update_path()

    def set_end_pos(self, pos):
        """Set temporary end position while dragging"""
        self.end_pos = pos
        self.update_path()

    def set_end_socket(self, socket):
        """Set the end socket when connection is complete"""
        self.end_socket = socket
        self.end_pos = None
        if socket:
            self.end_socket.edges.append(self)
        self.update_path()

    def update_path(self):
        """Update the edge path"""
        path = QPainterPath()

        # Get start position
        start_pos = self.start_socket.scenePos()

        # Get end position
        if self.end_socket:
            end_pos = self.end_socket.scenePos()
        elif self.end_pos:
            end_pos = self.end_pos
        else:
            return

        # Calculate control points
        dist = (end_pos.x() - start_pos.x()) * 0.5

        if self.start_socket.is_output:
            cp1 = QPointF(start_pos.x() + dist, start_pos.y())
            cp2 = QPointF(end_pos.x() - dist, end_pos.y())
        else:
            cp1 = QPointF(start_pos.x() - dist, start_pos.y())
            cp2 = QPointF(end_pos.x() + dist, end_pos.y())

        # Draw path
        path.moveTo(start_pos)
        path.cubicTo(cp1, cp2, end_pos)

        self.setPath(path)

    def paint(self, painter, option, widget=None):
        """Paint the edge"""
        if self.start_socket is None:
            return

        # Set pen
        pen = QPen(self.selected_color if self.isSelected() else self.color)
        pen.setWidthF(self.width)

        # Draw the path
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

    def remove(self):
        """Remove edge from scene and sockets"""
        if self.start_socket:
            self.start_socket.edges.remove(self)
        if self.end_socket:
            self.end_socket.edges.remove(self)
        self.scene().removeItem(self)

class EdgeDragHelper:
    def __init__(self, graphics_view):
        self.view = graphics_view
        self.dragging_edge = None
        self.last_mouse_pos = None

    def start_edge_drag(self, socket):
        """Start dragging a new edge from a socket"""
        self.dragging_edge = Edge(socket)
        self.view.scene().addItem(self.dragging_edge)

    def update_edge_drag(self, pos):
        """Update the dragging edge's end position"""
        if self.dragging_edge is not None:
            self.dragging_edge.temp_end_pos = pos
            self.dragging_edge.update_path()

    def end_edge_drag(self, target_socket=None):
        """End the edge drag, either connecting to a socket or removing the edge"""
        if self.dragging_edge is not None:
            if target_socket is not None:
                # Check if connection is valid
                if self.is_valid_connection(self.dragging_edge.start_socket, target_socket):
                    self.dragging_edge.set_end_socket(target_socket)
                else:
                    self.dragging_edge.remove()
            else:
                self.dragging_edge.remove()

            self.dragging_edge = None

    def is_valid_connection(self, start_socket, end_socket):
        """Check if the connection between two sockets is valid"""
        # Can't connect to self
        if start_socket.node == end_socket.node:
            return False

        # Can't connect input to input or output to output
        if start_socket.is_output == end_socket.is_output:
            return False

        # Can't create duplicate connections
        for edge in start_socket.edges:
            if edge.end_socket == end_socket:
                return False

        return True