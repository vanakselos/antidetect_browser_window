from ..node import Node
from PyQt6.QtWidgets import QMenu, QInputDialog, QMessageBox
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QPropertyAnimation


class CustomNode(Node):
    NODE_TYPE = "CustomNode"  # Override in subclasses

    def __init__(self, scene, title="Custom Node", inputs=None, outputs=None):
        super().__init__(scene, title, inputs or [], outputs or [])
        self.custom_data = {}
        self.status = "ready"  # ready, running, error
        self.animation = None

    def execute(self):
        """Override this method in subclasses"""
        try:
            self.set_status("running")
            result = self.do_execute()
            self.set_status("ready" if result else "error")
            return result
        except Exception as e:
            self.set_status("error")
            self.scene.logger.error(f"Error executing {self.title}: {str(e)}")
            return False

    def do_execute(self):
        """Implement custom execution logic in subclasses"""
        return True

    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        menu = QMenu()

        # Add standard actions
        delete_action = menu.addAction("Delete Node")
        copy_action = menu.addAction("Copy Node")
        configure_action = menu.addAction("Configure")

        # Add separator
        menu.addSeparator()

        # Add custom actions
        self.add_custom_menu_actions(menu)

        # Show menu and handle action
        action = menu.exec(event.screenPos())

        if action == delete_action:
            self.delete_node()
        elif action == copy_action:
            self.copy_node()
        elif action == configure_action:
            self.configure_node()

    def add_custom_menu_actions(self, menu):
        """Override to add custom menu actions"""
        pass

    def delete_node(self):
        """Delete this node and its connections"""
        reply = QMessageBox.question(
            None,
            "Delete Node",
            f"Are you sure you want to delete {self.title}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove all edges
            for socket in self.inputs + self.outputs:
                for edge in socket.edges[:]:  # Use copy of list
                    edge.remove()
            # Remove node
            self.scene.remove_node(self)

    def copy_node(self):
        """Create a copy of this node"""
        new_node = self.__class__(self.scene)
        new_node.custom_data = self.custom_data.copy()
        new_node.setPos(self.pos().x() + 50, self.pos().y() + 50)
        self.scene.add_node(new_node)

    def configure_node(self):
        """Open configuration dialog"""
        # Override in subclasses
        pass

    def set_status(self, status):
        """Set node status and update appearance"""
        self.status = status

        if status == "running":
            self.background_color = QColor("#4CAF50")  # Green
            self.start_animation()
        elif status == "error":
            self.background_color = QColor("#F44336")  # Red
            self.stop_animation()
        else:  # ready
            self.background_color = QColor("#E3212121")  # Default
            self.stop_animation()

        self.update()

    def start_animation(self):
        """Start edge flow animations"""
        for socket in self.outputs:
            for edge in socket.edges:
                edge.start_flow_animation()

    def stop_animation(self):
        """Stop edge flow animations"""
        for socket in self.outputs:
            for edge in socket.edges:
                edge.stop_flow_animation()

    def serialize(self):
        """Convert node to JSON-compatible dictionary"""
        return {
            'type': self.NODE_TYPE,
            'id': id(self),
            'title': self.title,
            'pos_x': self.pos().x(),
            'pos_y': self.pos().y(),
            'custom_data': self.custom_data,
            'inputs': [socket.serialize() for socket in self.inputs],
            'outputs': [socket.serialize() for socket in self.outputs]
        }

    def deserialize(self, data, hashmap={}):
        """Restore node from dictionary data"""
        self.setPos(data['pos_x'], data['pos_y'])
        self.title = data['title']
        self.custom_data = data.get('custom_data', {})

        # Restore connections in a second pass
        hashmap[data['id']] = self
        return True