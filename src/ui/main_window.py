from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from .profile_card import ProfileCard
from .create_profile_dialog import CreateProfileDialog
from ..utils.logger import get_logger


class MainWindow(QMainWindow):
    def __init__(self, browser_manager):
        super().__init__()
        self.browser_manager = browser_manager
        self.logger = get_logger(__name__)
        self.profile_cards = {}
        self.init_ui()
        self.load_profiles()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Anti-Detect Browser')
        self.setMinimumSize(1000, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create toolbar
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)

        # Create Profile button
        create_btn = QPushButton('Create Profile')
        create_btn.clicked.connect(self.show_create_profile_dialog)
        create_btn.setFixedWidth(150)
        toolbar_layout.addWidget(create_btn)

        # Add stretch to push buttons to the left
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar_widget)

        # Create scroll area for profiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create widget for profiles grid
        self.profiles_widget = QWidget()
        self.profiles_layout = QVBoxLayout(self.profiles_widget)
        self.profiles_layout.setSpacing(10)
        self.profiles_layout.setContentsMargins(10, 10, 10, 10)

        scroll.setWidget(self.profiles_widget)
        main_layout.addWidget(scroll)

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        # You can load styles from QSS file or define them here
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#profiles_widget {
                background-color: transparent;
            }
        """)

    def show_create_profile_dialog(self):
        dialog = CreateProfileDialog(self)
        if dialog.exec():
            profile_name = dialog.get_profile_name()
            if profile_name:
                self.create_profile(profile_name)

    def create_profile(self, profile_name: str):
        try:
            if self.browser_manager.create_profile(profile_name):
                self.add_profile_card(profile_name)
                QMessageBox.information(self, "Success", f"Profile '{profile_name}' created successfully")
            else:
                QMessageBox.warning(self, "Error", f"Failed to create profile '{profile_name}'")
        except Exception as e:
            self.logger.error(f"Error creating profile: {e}")
            QMessageBox.critical(self, "Error", f"Error creating profile: {str(e)}")

    def add_profile_card(self, profile_name: str):
        try:
            profile = self.browser_manager.profile_manager.get_profile(profile_name)
            if profile:
                card = ProfileCard(profile, self.browser_manager)
                self.profile_cards[profile_name] = card
                self.profiles_layout.addWidget(card)
        except Exception as e:
            self.logger.error(f"Error adding profile card: {e}")

    def load_profiles(self):
        try:
            profiles = self.browser_manager.profile_manager.get_all_profiles()
            for profile_name in profiles:
                self.add_profile_card(profile_name)
        except Exception as e:
            self.logger.error(f"Error loading profiles: {e}")
            QMessageBox.critical(self, "Error", f"Error loading profiles: {str(e)}")

    def closeEvent(self, event):
        try:
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'Are you sure you want to exit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.browser_manager.cleanup()
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            self.logger.error(f"Error during close: {e}")
            event.accept()