import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.core.browser_manager import BrowserManager
from src.utils.config import Config
from src.utils.logger import setup_logger, get_logger
import atexit


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = Config()
        self.logger = setup_logger()
        self.browser_manager = BrowserManager()
        self.main_window = MainWindow(self.browser_manager)

        # Register cleanup
        atexit.register(self.cleanup)

    def run(self):
        self.main_window.show()
        return self.app.exec()

    def cleanup(self):
        self.browser_manager.cleanup()


def main():
    app = Application()
    return app.run()



if __name__ == "__main__":
    sys.exit(main())