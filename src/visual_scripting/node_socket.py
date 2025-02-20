# node_socket.py
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from enum import Enum


class Socket(QGraphicsItem):
    class Type(Enum):
        INPUT = 1
        OUTPUT = 2

    class Position(Enum):
        LEFT_TOP = 1
        LEFT_BOTTOM = 2
        RIGHT_TOP = 3
        RIGHT_BOTTOM = 4

    def __init__(self, node, index=0, position=Position.LEFT_TOP,
                 socket_type=Type.INPUT, label=""):
        super().__init__(node)
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.label = label

        # Visual properties
        self.radius = 8
        self.outline_width = 1
        self.edges = []

        # Colors
        self.color_background = QColor("#FF212121")
        self.color_outline = QColor("#FF666666")
        self.color_connected = QColor("#FF00FF00")

        # Make sure socket is selectable and can receive hover events
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # Calculate position
        self.update_position()

    def boundingRect(self) -> QRectF:
        # Make clickable area larger than visual socket
        extra_space = 4
        return QRectF(
            -self.radius - self.outline_width - extra_space,
            -self.radius - self.outline_width - extra_space,
            2 * (self.radius + self.outline_width + extra_space),
            2 * (self.radius + self.outline_width + extra_space)
        )


    def paint(self, painter: QPainter, option, widget=None):
        # Background
        painter.setBrush(QBrush(
            self.color_connected if self.edges else self.color_background
        ))
        painter.setPen(QPen(self.color_outline, self.outline_width))
        painter.drawEllipse(
            -self.radius, -self.radius,
            2 * self.radius, 2 * self.radius
        )

    def update_position(self):
        """Update socket position based on its type and index"""
        x = 0 if self.socket_type == Socket.Type.INPUT else self.node.width
        y = self.node.title_height + self.index * self.node.socket_spacing
        self.setPos(x, y)

    @property
    def is_output(self):
        return self.socket_type == Socket.Type.OUTPUT

    @property
    def is_input(self):
        return self.socket_type == Socket.Type.INPUT

    def shape(self):
        # Define precise clickable area
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def mousePressEvent(self, event):
        """Handle mouse press on socket"""
        print(f"Socket clicked: {self.label} of type {self.socket_type}")
        super().mousePressEvent(event)