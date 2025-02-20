from PyQt6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation
from PyQt6.QtWidgets import QGraphicsItem, QMenu, QInputDialog
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from typing import List, Optional
from .node_socket import Socket
import json


class Node(QGraphicsItem):
    def __init__(self, scene, title: str = "Node", inputs: List[str] = None, outputs: List[str] = None):
        super().__init__()
        self.scene = scene
        self.title = title
        self.width = 180
        self.height = 100
        self.socket_spacing = 22

        # Visual settings
        self.title_height = 24
        self.title_color = Qt.GlobalColor.white
        self.title_background = QColor("#FF313131")
        self.background_color = QColor("#E3212121")

        # Flags for interaction
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # For dragging
        self.last_pos = None

        # Create sockets
        self.inputs: List[Socket] = []
        self.outputs: List[Socket] = []
        self.init_sockets(inputs or [], outputs or [])

    def execute(self):
        """Base execute method"""
        try:
            if not self.scene.current_profile:
                raise ValueError("No profile selected")

            self.is_running = True
            self.update()

            result = self.do_execute()
            return result

        except Exception as e:
            self.scene.logger.error(f"Error executing {self.title}: {str(e)}")
            return False

        finally:
            self.is_running = False
            self.update()

    def do_execute(self):
        """Override this in child nodes"""
        return True

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        print("Node mouse press")
        if event.button() == Qt.MouseButton.LeftButton:
            print("Node mouse press left")
            print(event)

            print(event.scenePos())

            self.last_pos = event.scenePos()
            print("Node mouse press left1")

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        print("Node mouse move")
        if event.buttons() & Qt.MouseButton.LeftButton:
            print("Node mouse move1")
            print(event)
            print("pos", event.scenePos())
            if self.last_pos:
                # Calculate delta movement
                delta = event.scenePos() - self.last_pos
                self.moveBy(delta.x(), delta.y())
                self.last_pos = event.scenePos()

                # Update connected edges
                for socket in self.inputs + self.outputs:
                    for edge in socket.edges:
                        edge.update_path()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release after dragging"""
        print("Node mouse release")
        self.last_pos = None
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # Update connected edges when node moves
            for socket in self.inputs + self.outputs:
                for edge in socket.edges:
                    edge.update_path()
        return super().itemChange(change, value)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        # Title background
        painter.setBrush(QBrush(self.title_background))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width, self.title_height)

        # Title
        painter.setPen(QPen(self.title_color))
        painter.setFont(self.scene.font)
        painter.drawText(
            QRectF(0, 0, self.width, self.title_height),
            Qt.AlignmentFlag.AlignCenter,
            self.title
        )

        # Content background
        painter.setBrush(QBrush(self.background_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, self.title_height, self.width,
                         self.height - self.title_height)

        # Draw outline when selected
        if self.isSelected():
            painter.setPen(QPen(QColor("#FFFFA637"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(0, 0, self.width, self.height)

    def init_sockets(self, inputs: List[str], outputs: List[str]):
        # Create input sockets
        if inputs:
            for i, label in enumerate(inputs):
                socket = Socket(
                    node=self,
                    index=i,
                    position=Socket.Position.LEFT_TOP,
                    socket_type=Socket.Type.INPUT,
                    label=label
                )
                self.inputs.append(socket)

        # Create output sockets
        if outputs:
            for i, label in enumerate(outputs):
                socket = Socket(
                    node=self,
                    index=i,
                    position=Socket.Position.RIGHT_TOP,
                    socket_type=Socket.Type.OUTPUT,
                    label=label
                )
                self.outputs.append(socket)

    def add_socket(self, label: str, socket_type: Socket.Type):
        """Add a new socket to the node"""
        if socket_type == Socket.Type.INPUT:
            socket = Socket(
                node=self,
                index=len(self.inputs),
                position=Socket.Position.LEFT_TOP,
                socket_type=Socket.Type.INPUT,
                label=label
            )
            self.inputs.append(socket)
        else:
            socket = Socket(
                node=self,
                index=len(self.outputs),
                position=Socket.Position.RIGHT_TOP,
                socket_type=Socket.Type.OUTPUT,
                label=label
            )
            self.outputs.append(socket)
        return socket

    def remove_socket(self, socket: Socket):
        """Remove a socket from the node"""
        if socket in self.inputs:
            self.inputs.remove(socket)
        elif socket in self.outputs:
            self.outputs.remove(socket)
        # Update indices of remaining sockets
        self.update_socket_indices()

    def update_socket_indices(self):
        """Update the indices of all sockets after adding/removing"""
        for i, socket in enumerate(self.inputs):
            socket.index = i
            socket.update_position()
        for i, socket in enumerate(self.outputs):
            socket.index = i
            socket.update_position()

    def get_socket_position(self, socket: Socket) -> QPointF:
        """Get the absolute position of a socket"""
        return self.pos() + socket.pos()


    def set_status(self, status):
        """Set node status and update appearance"""
        self.status = status

        if status == "running":
            self.background_color = QColor("#4CAF50")  # Green
            # self.start_animation()
        elif status == "error":
            self.background_color = QColor("#F44336")  # Red
            # self.stop_animation()
        else:  # ready
            self.background_color = QColor("#E3212121")  # Default
            # self.stop_animation()

        self.update()

    def get_current_profile(self):
        """Get the currently selected profile"""
        return self.scene.current_profile