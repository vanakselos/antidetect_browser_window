from PyQt6.QtWidgets import QGraphicsScene, QMessageBox
from PyQt6.QtGui import QFont, QColor, QPen, QPainter
from PyQt6.QtCore import Qt, QLineF, QRectF, QPointF
from typing import List, Optional
from .node import Node
from .node_edge import Edge
from .node_socket import Socket
from .nodes.start_node import StartNode
import json
from ..utils.logger import get_logger


class NodeScene(QGraphicsScene):
    def __init__(self, browser_manager, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.font = QFont("Ubuntu", 10)
        self.browser_manager = browser_manager

        # Lists of nodes and edges
        self.current_profile = None  # Store current profile
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

        # Grid settings
        self.grid_size = 20.0
        self.grid_squares = 5
        self.grid_color = QColor("#2F2F2F")
        self.grid_color_dark = QColor("#292929")

        # Edge drawing state
        self.dragging_edge = None
        self.dragging_start_socket = None

        self.init_ui()

    def mousePressEvent(self, event):
        """Handle mouse press in scene"""
        pos = event.scenePos()
        items = self.items(pos)

        # Debug print
        print("Scene mouse press, items:", items)
        print("Event type:", type(event))

        # Check for socket first
        clicked_socket = None
        clicked_node = None

        for item in items:
            if isinstance(item, Socket):
                clicked_socket = item
                break
            elif isinstance(item, Node):
                clicked_node = item
            # Check parent item
            parent = item.parentItem() if hasattr(item, 'parentItem') else None
            if isinstance(parent, Socket):
                clicked_socket = parent
                break

        if clicked_socket and event.button() == Qt.MouseButton.LeftButton:
            print("Socket found:", clicked_socket)
            # Start drawing an edge
            self.dragging_start_socket = clicked_socket
            self.dragging_edge = Edge(self.dragging_start_socket)
            self.addItem(self.dragging_edge)
            event.accept()
            return

        # If no socket was clicked, let the event propagate for node dragging
        super().mousePressEvent(event)


    def init_ui(self):
        # Set scene size and background
        self.setBackgroundBrush(QColor("#1A1A1A"))  # Darker background
        self.setSceneRect(-50000.0, -50000.0, 100000.0, 100000.0)

    def mouseMoveEvent(self, event):
        """Handle mouse move in scene"""
        if self.dragging_edge:
            # Update edge end position
            self.dragging_edge.set_end_pos(event.scenePos())
            self.dragging_edge.update()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release in scene"""
        if self.dragging_edge and event.button() == Qt.MouseButton.LeftButton:
            # Find target socket
            pos = event.scenePos()
            items = self.items(pos)

            target_socket = None
            for item in items:
                if isinstance(item, Socket):
                    target_socket = item
                    break
                parent = item.parentItem() if hasattr(item, 'parentItem') else None
                if isinstance(parent, Socket):
                    target_socket = parent
                    break

            if target_socket and self.validate_edge_connection(self.dragging_start_socket, target_socket):
                self.dragging_edge.set_end_socket(target_socket)
            else:
                self.removeItem(self.dragging_edge)

            self.dragging_edge = None
            self.dragging_start_socket = None
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def validate_edge_connection(self, start_socket, end_socket):
        """Validate if two sockets can be connected"""
        if start_socket.node == end_socket.node:
            return False
        if start_socket.socket_type == end_socket.socket_type:
            return False
        return True


    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Draw custom grid background"""
        super().drawBackground(painter, rect)

        # Create grid
        left = rect.left() - (rect.left() % self.grid_size)
        top = rect.top() - (rect.top() % self.grid_size)
        right = rect.right()
        bottom = rect.bottom()

        # Draw grid lines
        grid_width = 1.0
        grid_width_dark = 2.0

        # Create pens for different grid lines
        small_pen = QPen(self.grid_color)
        small_pen.setWidthF(grid_width)
        dark_pen = QPen(self.grid_color_dark)
        dark_pen.setWidthF(grid_width_dark)

        # Draw vertical lines
        x = left
        while x < right:
            if abs(x % (self.grid_size * self.grid_squares)) < 0.001:
                painter.setPen(dark_pen)
            else:
                painter.setPen(small_pen)
            line = QLineF(x, top, x, bottom)
            painter.drawLine(line)
            x += self.grid_size

        # Draw horizontal lines
        y = top
        while y < bottom:
            if abs(y % (self.grid_size * self.grid_squares)) < 0.001:
                painter.setPen(dark_pen)
            else:
                painter.setPen(small_pen)
            line = QLineF(left, y, right, y)
            painter.drawLine(line)
            y += self.grid_size

    def add_node(self, node: Node):
        # Snap to grid with float precision
        node_pos = node.pos()
        node.setPos(
            round(node_pos.x() / self.grid_size) * self.grid_size,
            round(node_pos.y() / self.grid_size) * self.grid_size
        )
        self.nodes.append(node)
        self.addItem(node)

    def remove_node(self, node: Node):
        self.nodes.remove(node)
        self.removeItem(node)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        self.addItem(edge)

    def remove_edge(self, edge: Edge):
        self.edges.remove(edge)
        self.removeItem(edge)

    def clear(self):
        """Clear all nodes and edges from the scene"""
        for node in self.nodes[:]:
            self.remove_node(node)
        for edge in self.edges[:]:
            self.remove_edge(edge)

    def get_grid_position(self, pos: QPointF) -> QPointF:
        """Convert any position to nearest grid position"""
        return QPointF(
            round(pos.x() / self.grid_size) * self.grid_size,
            round(pos.y() / self.grid_size) * self.grid_size
        )

    def set_grid_size(self, size: float):
        """Change grid size"""
        self.grid_size = size
        self.update()

    def set_grid_squares(self, squares: int):
        """Change number of squares between dark lines"""
        self.grid_squares = squares
        self.update()

    def set_grid_colors(self, main_color: QColor, dark_color: QColor):
        """Change grid colors"""
        self.grid_color = main_color
        self.grid_color_dark = dark_color
        self.update()

    def set_grid_appearance(self,
                            grid_size: float = 20.0,
                            grid_squares: int = 5,
                            main_color: str = "#2F2F2F",
                            dark_color: str = "#292929"):
        """Set all grid appearance properties at once"""
        self.grid_size = grid_size
        self.grid_squares = grid_squares
        self.grid_color = QColor(main_color)
        self.grid_color_dark = QColor(dark_color)
        self.update()

    def zoom_grid(self, factor: float):
        """Zoom grid in or out"""
        self.grid_size *= factor
        self.update()

    def save_workflow(self, filename):
        """Save workflow to JSON file"""
        data = {
            'nodes': [node.serialize() for node in self.nodes],
            'edges': [edge.serialize() for edge in self.edges]
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving workflow: {str(e)}")
            return False

    def load_workflow(self, filename):
        """Load workflow from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Clear current scene
            self.clear()

            # Create nodes
            hashmap = {}
            for node_data in data['nodes']:
                node_type = node_data['type']
                node_class = self.get_node_class(node_type)
                if node_class:
                    node = node_class(self)
                    node.deserialize(node_data, hashmap)
                    self.add_node(node)

            # Create edges
            for edge_data in data['edges']:
                start_socket = hashmap[edge_data['start_socket']]
                end_socket = hashmap[edge_data['end_socket']]
                edge = Edge(start_socket, end_socket)
                self.add_edge(edge)

            return True

        except Exception as e:
            self.logger.error(f"Error loading workflow: {str(e)}")
            return False

    def get_node_class(self, node_type):
        """Get node class by type"""
        # Add your custom nodes here
        node_classes = {
            'CalculatorNode': CalculatorNode,
            # Add more node types
        }
        return node_classes.get(node_type)

    def execute_workflow(self, start_node=None):

        """Execute workflow with current profile"""
        if not self.current_profile:
            raise ValueError("No profile selected")

        """Execute workflow starting from the given start node"""
        if not start_node:
            # Find first start node
            start_nodes = [node for node in self.nodes
                           if isinstance(node, StartNode)]
            if not start_nodes:
                QMessageBox.warning(
                    None,
                    "Execution Error",
                    "No Start node found in workflow."
                )
                return False
            start_node = start_nodes[0]

        try:
            # Clear any previous execution states
            self.clear_execution_states()

            # Execute the workflow
            result = self.execute_node(start_node)

            if result:
                QMessageBox.information(
                    None,
                    "Execution Complete",
                    "Workflow executed successfully!"
                )
            else:
                QMessageBox.warning(
                    None,
                    "Execution Error",
                    "Workflow execution failed. Check the logs for details."
                )

            return result

        except Exception as e:
            self.logger.error(f"Workflow execution error: {str(e)}")
            QMessageBox.critical(
                None,
                "Execution Error",
                f"Error executing workflow: {str(e)}"
            )
            return False
        finally:
            self.clear_execution_states()

    def clear_execution_states(self):
        """Clear execution states of all nodes"""
        for node in self.nodes:
            node.is_running = False
            # Stop any animations
            if hasattr(node, 'stop_animation'):
                node.stop_animation()
        self.update()

    def execute_node(self, node):
        """Execute a single node and its outputs"""
        if not node.execute():
            return False

        # Execute connected nodes
        for socket in node.outputs:
            for edge in socket.edges:
                next_node = edge.end_socket.node
                if not self.execute_node(next_node):
                    return False

        return True