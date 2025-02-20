# src/visual_scripting/nodes/start_node.py
from ..node import Node
from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QRadialGradient, QPainterPath
from PyQt6.QtCore import Qt, QRectF


class StartNode(Node):
    NODE_TYPE = "StartNode"

    def __init__(self, scene):
        super().__init__(
            scene,
            title="Start",
            inputs=[],  # Start node has no inputs
            outputs=["Next"]  # Only one output
        )
        # Visual settings
        self.width = 120  # Make it smaller than standard nodes
        self.height = 80
        self.title_height = 30

        # Colors
        self.title_background = QColor("#2E7D32")  # Dark green
        self.background_color = QColor("#4CAF50")  # Light green
        self.outline_color = QColor("#81C784")  # Lighter green

        # Animation properties
        self._pulse_factor = 0.0
        self.is_running = False

        # Tooltip
        self.setToolTip("Start node - Beginning of workflow - Right click to select profile and run")

    def do_execute(self):
        """Implement specific execution logic for Start node"""
        try:
            # Execute all connected nodes through output socket
            for socket in self.outputs:
                for edge in socket.edges:
                    next_node = edge.end_socket.node
                    if not next_node.execute():
                        return False
            return True
        except Exception as e:
            self.scene.logger.error(f"Error in Start node execution: {str(e)}")
            return False

    def paint(self, painter: QPainter, option, widget=None):
        """Custom paint for start node with special effects"""
        # Draw background with gradient
        gradient = QRadialGradient(
            self.width / 2, self.height / 2,
            max(self.width, self.height)
        )
        gradient.setColorAt(0, self.background_color)
        gradient.setColorAt(1, self.background_color.darker(120))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw rounded rectangle
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)

        # Draw title background
        title_path = QPainterPath()
        title_path.addRoundedRect(0, 0, self.width, self.title_height, 10, 10)
        painter.fillPath(title_path, QBrush(self.title_background))

        # Draw title
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(self.scene.font)
        painter.drawText(
            QRectF(0, 0, self.width, self.title_height),
            Qt.AlignmentFlag.AlignCenter,
            self.title
        )

        # Draw status indicator
        if self.is_running:
            painter.setPen(Qt.PenStyle.NoPen)
            indicator_gradient = QRadialGradient(
                self.width - 15, 15, 8
            )
            indicator_gradient.setColorAt(0, QColor("#4CAF50"))
            indicator_gradient.setColorAt(1, QColor("#2E7D32"))
            painter.setBrush(QBrush(indicator_gradient))
            painter.drawEllipse(self.width - 20, 10, 10, 10)

        # Draw outline when selected
        if self.isSelected():
            painter.setPen(QPen(self.outline_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)

    def execute(self):
        """Execute the start node"""
        try:
            self.is_running = True
            self.scene.update()

            for socket in self.outputs:
                for edge in socket.edges:
                    next_node = edge.end_socket.node
                    if not next_node.execute():
                        return False

            return True

        except Exception as e:
            self.scene.logger.error(f"Error in Start node: {str(e)}")
            return False
        finally:
            self.is_running = False
            self.scene.update()

    def contextMenuEvent(self, event):
        """Handle right-click menu"""
        menu = QMenu()

        # Add actions
        run_action = menu.addAction("Run Workflow")
        menu.addSeparator()
        copy_action = menu.addAction("Copy Node")

        # Show menu and handle action
        action = menu.exec(event.screenPos())

        if action == run_action:
            self.scene.execute_workflow(self)
        elif action == copy_action:
            self.copy_node()

    def can_be_deleted(self) -> bool:
        """Prevent deletion if this is the only start node"""
        start_nodes = [node for node in self.scene.nodes
                       if isinstance(node, StartNode)]
        return len(start_nodes) > 1

    def delete_node(self):
        """Override delete to prevent deletion of last start node"""
        if not self.can_be_deleted():
            QMessageBox.warning(
                None,
                "Cannot Delete",
                "Cannot delete the only Start node in the workflow."
            )
            return

        super().delete_node()

    def serialize(self):
        """Convert node to JSON-compatible dictionary"""
        data = super().serialize()
        data['node_type'] = self.NODE_TYPE
        return data

    @classmethod
    def deserialize(cls, scene, data):
        """Create a new Start node from serialized data"""
        node = cls(scene)
        node.setPos(data['pos_x'], data['pos_y'])
        return node