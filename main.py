import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.core.browser_manager import BrowserManager
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.visual_scripting.node_editor import NodeEditorWidget
import atexit


class CombinedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anti-Detect Browser with Visual Scripting")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create splitter for browser and node editor
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Initialize components
        self.config = Config()
        self.logger = setup_logger()
        self.browser_manager = BrowserManager()

        # Create browser window
        self.browser_window = MainWindow(self.browser_manager)
        splitter.addWidget(self.browser_window)

        # Create node editor
        self.node_editor = NodeEditorWidget(self.browser_manager)
        splitter.addWidget(self.node_editor)

        # Set initial splitter sizes (50-50 split)
        splitter.setSizes([600, 600])

        # Add splitter to layout
        layout.addWidget(splitter)

        # Register cleanup
        atexit.register(self.cleanup)

        # Add menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        # Add actions to file menu
        new_action = file_menu.addAction('New Script')
        new_action.triggered.connect(self.new_script)

        save_action = file_menu.addAction('Save Script')
        save_action.triggered.connect(self.save_script)

        load_action = file_menu.addAction('Load Script')
        load_action.triggered.connect(self.load_script)

        # Add separator
        file_menu.addSeparator()

        # Exit action
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)

        # Script menu
        script_menu = menubar.addMenu('Script')

        run_action = script_menu.addAction('Run')
        run_action.triggered.connect(self.run_script)

        stop_action = script_menu.addAction('Stop')
        stop_action.triggered.connect(self.stop_script)

    def new_script(self):
        # Clear the node editor
        self.node_editor.scene.clear()

    def save_script(self):
        # TODO: Implement save functionality
        pass

    def load_script(self):
        # TODO: Implement load functionality
        pass

    def run_script(self):
        self.node_editor.execute_workflow()

    def stop_script(self):
        # TODO: Implement stop functionality
        pass

    def cleanup(self):
        try:
            self.browser_manager.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def main():
    # Create necessary directories
    for directory in ['logs', 'profiles']:
        if not os.path.exists(directory):
            os.makedirs(directory)

    try:
        app = QApplication(sys.argv)
        window = CombinedWindow()
        window.show()
        return app.exec()
    except Exception as e:
        print(f"Error running application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
