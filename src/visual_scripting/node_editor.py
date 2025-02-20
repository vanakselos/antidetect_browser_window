from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGraphicsItem,
                             QMenu, QToolBar, QMessageBox,
                             QInputDialog, QColorDialog, QToolButton)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsView, QLabel, QComboBox
from PyQt6.QtGui import QPainter, QAction
from .node_scene import NodeScene
from .nodes.navigation_nodes import OpenUrlNode, ScrollNode, LikePostNode
from .nodes.start_node import StartNode
from ..utils.logger import get_logger


class NodeEditorWidget(QWidget):
    def __init__(self, browser_manager, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.browser_manager = browser_manager

        # Create scene and view
        self.scene = NodeScene(browser_manager=self.browser_manager)
        self.view = QGraphicsView(self.scene)

        # Track execution state
        self.is_running = False
        self.current_executing_node = None

        # Edge drawing state
        self.dragging_edge = None
        self.dragging_start_socket = None
        self.dragging_node = None

        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 200, 800, 600)

        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # Add view
        layout.addWidget(self.view)

        # Setup view
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def add_node(self, node_class):
        node = node_class(self.scene)
        node.setPos(self.view.mapToScene(
            self.view.viewport().width() // 2,
            self.view.viewport().height() // 2
        ))
        self.scene.add_node(node)

    def execute_workflow(self):

        if not self.scene.current_profile:
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Please select a profile before running the workflow."
            )
            return

        """Execute the workflow from start to finish"""
        if self.is_running:
            self.logger.warning("Workflow is already running")
            return

        self.is_running = True

        # Find start node
        start_node = next(
            (node for node in self.scene.nodes if isinstance(node, StartNode)),
            None
        )

        if not start_node:
            QMessageBox.warning(self, "Error", "No start node found!")
            self.is_running = False
            return

        try:
            self.execute_node(start_node)
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            QMessageBox.critical(self, "Error", f"Execution failed: {str(e)}")
        finally:
            self.is_running = False
            self.current_executing_node = None

    def execute_node(self, node):

        if not self.scene.current_profile:
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Please select a profile before running the workflow."
            )
            return

        """Execute a single node and its outputs"""
        if not self.is_running:
            return False

        self.current_executing_node = node

        # Highlight current node
        node.setSelected(True)
        self.view.update()

        # Execute current node
        try:
            if not node.execute():
                return False
        finally:
            node.setSelected(False)

        # Find and execute next node
        for output in node.outputs:
            print("output", output)
            for edge in output.edges:
                next_node = edge.end_socket.node
                self.execute_node(next_node)

        return True

    def stop_workflow(self):
        """Stop the currently running workflow"""
        self.is_running = False
        if self.current_executing_node:
            self.current_executing_node.setSelected(False)
            self.current_executing_node = None
        self.logger.info("Workflow execution stopped")
        QMessageBox.information(self, "Stopped", "Workflow execution has been stopped")


    def clear(self):
        """Clear all nodes and edges"""
        self.scene.clear()
        self.logger.info("Node editor cleared")

    def create_toolbar(self):
        toolbar = QToolBar()

        # Create Grid Menu Button
        grid_button = QToolButton()
        grid_button.setText("Grid")
        grid_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        grid_menu = QMenu()

        # Grid size
        grid_size_action = QAction("Grid Size", self)
        grid_size_action.triggered.connect(self.change_grid_size)
        grid_menu.addAction(grid_size_action)

        # Grid squares
        grid_squares_action = QAction("Grid Squares", self)
        grid_squares_action.triggered.connect(self.change_grid_squares)
        grid_menu.addAction(grid_squares_action)

        # Grid colors
        grid_colors_action = QAction("Grid Colors", self)
        grid_colors_action.triggered.connect(self.change_grid_colors)
        grid_menu.addAction(grid_colors_action)

        grid_button.setMenu(grid_menu)
        toolbar.addWidget(grid_button)

        # Add profile selector
        profile_label = QLabel("Profile: ")
        toolbar.addWidget(profile_label)

        self.profile_selector = QComboBox()
        self.profile_selector.setMinimumWidth(150)
        self.update_profile_list()
        self.profile_selector.currentTextChanged.connect(self.on_profile_changed)
        toolbar.addWidget(self.profile_selector)

        # Add separator
        toolbar.addSeparator()

        # Add node creation actions
        toolbar.addAction("Start Node", lambda: self.add_node(StartNode))
        toolbar.addAction("Open URL", lambda: self.add_node(OpenUrlNode))
        toolbar.addAction("Scroll", lambda: self.add_node(ScrollNode))
        toolbar.addAction("Like Post", lambda: self.add_node(LikePostNode))

        # Add execution controls
        toolbar.addSeparator()
        toolbar.addAction("Run", self.execute_workflow)
        toolbar.addAction("Stop", self.stop_workflow)

        return toolbar

    def update_profile_list(self):
        """Update the profile selector with current profiles"""
        self.profile_selector.clear()
        self.profile_selector.addItem("Select Profile")  # Default option
        if hasattr(self.browser_manager, 'profile_manager'):
            for profile_name in self.browser_manager.profile_manager.profiles.keys():
                print("Profile", profile_name)
                self.profile_selector.addItem(profile_name)

    def on_profile_changed(self, profile_name):
        """Handle profile selection change"""
        if profile_name != "Select Profile":
            self.scene.current_profile = profile_name
        else:
            self.scene.current_profile = None
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Please select a profile before running the workflow."
            )
            return

    def change_grid_size(self):
        size, ok = QInputDialog.getDouble(
            self, "Grid Size", "Enter grid size:",
            self.scene.grid_size, 5.0, 100.0, 1
        )
        if ok:
            self.scene.set_grid_size(size)

    def change_grid_squares(self):
        squares, ok = QInputDialog.getInt(
            self, "Grid Squares", "Enter number of squares between dark lines:",
            self.scene.grid_squares, 1, 20
        )
        if ok:
            self.scene.set_grid_squares(squares)

    def change_grid_colors(self):
        color = QColorDialog.getColor(
            self.scene.grid_color, self, "Choose Grid Color"
        )
        if color.isValid():
            dark_color = QColorDialog.getColor(
                self.scene.grid_color_dark, self, "Choose Dark Grid Color"
            )
            if dark_color.isValid():
                self.scene.set_grid_colors(color, dark_color)