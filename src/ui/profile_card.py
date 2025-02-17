from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMenu, QMessageBox)
from PyQt6.QtCore import Qt
from ..utils.logger import get_logger


class ProfileCard(QFrame):
    def __init__(self, profile, browser_manager, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.browser_manager = browser_manager
        self.logger = get_logger(__name__)
        self.init_ui()

    def init_ui(self):
        try:
            # Set frame properties
            self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
            self.setLineWidth(1)

            # Main layout
            layout = QVBoxLayout(self)
            layout.setSpacing(10)

            # Profile header
            header_layout = QHBoxLayout()

            # Profile name
            name_label = QLabel(f"<b>{self.profile.name}</b>")
            name_label.setStyleSheet("font-size: 14px;")
            header_layout.addWidget(name_label)

            # Menu button
            menu_button = QPushButton("⋮")
            menu_button.setFixedWidth(30)
            menu_button.clicked.connect(self.show_menu)
            header_layout.addWidget(menu_button)

            layout.addLayout(header_layout)

            # Profile info
            info_layout = QVBoxLayout()

            # User Agent
            ua_label = QLabel(f"<b>User Agent:</b> {self.profile.fingerprint.get('user_agent', 'N/A')[:50]}...")
            ua_label.setWordWrap(True)
            info_layout.addWidget(ua_label)

            # Platform
            platform_label = QLabel(f"<b>Platform:</b> {self.profile.fingerprint.get('platform', 'N/A')}")
            info_layout.addWidget(platform_label)

            # Language
            lang_label = QLabel(f"<b>Language:</b> {self.profile.fingerprint.get('language', 'N/A')}")
            info_layout.addWidget(lang_label)

            layout.addLayout(info_layout)

            # Buttons
            button_layout = QHBoxLayout()

            # Launch button
            launch_btn = QPushButton("Launch Browser")
            launch_btn.clicked.connect(self.launch_browser)
            button_layout.addWidget(launch_btn)

            layout.addLayout(button_layout)

            # Apply styles
            self.apply_styles()

        except Exception as e:
            self.logger.error(f"Error initializing profile card UI: {e}")
            raise

    def apply_styles(self):
        self.setStyleSheet("""
            ProfileCard {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
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
            QPushButton[text="⋮"] {
                background-color: transparent;
                color: #333;
                font-weight: bold;
            }
            QPushButton[text="⋮"]:hover {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
        """)

    def show_menu(self):
        menu = QMenu(self)

        # Add menu actions
        edit_action = menu.addAction("Edit Profile")
        export_action = menu.addAction("Export Profile")
        delete_action = menu.addAction("Delete Profile")

        # Add separator
        menu.addSeparator()

        # Add proxy settings
        proxy_action = menu.addAction("Configure Proxy")

        # Connect actions to slots
        edit_action.triggered.connect(self.edit_profile)
        export_action.triggered.connect(self.export_profile)
        delete_action.triggered.connect(self.delete_profile)
        proxy_action.triggered.connect(self.configure_proxy)

        # Show menu
        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    def launch_browser(self):
        try:
            if self.browser_manager.launch_profile(self.profile.name):
                self.logger.info(f"Successfully launched profile: {self.profile.name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to launch browser")
        except Exception as e:
            self.logger.error(f"Error launching browser: {e}")
            QMessageBox.critical(self, "Error", f"Error launching browser: {str(e)}")

    def edit_profile(self):
        # TODO: Implement profile editing
        QMessageBox.information(self, "Info", "Profile editing coming soon")

    def export_profile(self):
        try:
            # TODO: Implement profile export
            QMessageBox.information(self, "Info", "Profile export coming soon")
        except Exception as e:
            self.logger.error(f"Error exporting profile: {e}")
            QMessageBox.critical(self, "Error", f"Error exporting profile: {str(e)}")

    def delete_profile(self):
        try:
            reply = QMessageBox.question(
                self, 'Confirm Delete',
                f'Are you sure you want to delete profile "{self.profile.name}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # TODO: Implement profile deletion
                QMessageBox.information(self, "Info", "Profile deletion coming soon")
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
            QMessageBox.critical(self, "Error", f"Error deleting profile: {str(e)}")

    def configure_proxy(self):
        # TODO: Implement proxy configuration
        QMessageBox.information(self, "Info", "Proxy configuration coming soon")