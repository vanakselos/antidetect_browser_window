from ..node import Node
from PyQt6.QtWidgets import (QMenu, QInputDialog, QMessageBox,
                            QDialog, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QLabel)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt


class UrlConfigDialog(QDialog):
    def __init__(self, current_url="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure URL")
        self.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(self)

        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit(current_url)
        self.url_input.setPlaceholderText("https://example.com")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Quick URL buttons
        quick_urls_layout = QHBoxLayout()
        quick_urls = [
            ("Google", "https://www.google.com"),
            ("Facebook", "https://www.facebook.com"),
            ("YouTube", "https://www.youtube.com")
        ]

        for label, url in quick_urls:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, u=url: self.url_input.setText(u))
            quick_urls_layout.addWidget(btn)

        layout.addLayout(quick_urls_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                padding: 5px;
                background-color: #3b3b3b;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton[text="Cancel"] {
                background-color: #666666;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #777777;
            }
        """)

    def get_url(self):
        return self.url_input.text().strip()


class OpenUrlNode(Node):
    def __init__(self, scene):
        super().__init__(
            scene,
            title="Open URL",
            inputs=["Trigger"],
            outputs=["Next"]
        )
        self.url = ""
        self.background_color = QColor("#1A237E")  # Dark blue

    def do_execute(self):
        try:
            if not self.url:
                raise ValueError("URL not configured")

            # Set status to running
            self.set_status("running")

            # Get current profile
            profile_name = self.get_current_profile()
            print("=============", profile_name)
            if not profile_name:
                raise ValueError("No profile selected")

            # Validate URL
            if not self.url.startswith(('http://', 'https://')):
                self.url = 'https://' + self.url

            # Get the browser instance from scene
            if hasattr(self.scene, 'browser_manager'):
                browser = self.scene.browser_manager.get_browser(profile_name)
                browser.driver.get(self.url)
                return True
            else:
                raise ValueError("Browser manager not initialized")

        except Exception as e:
            self.scene.logger.error(f"Error opening URL: {str(e)}")
            return False

    def configure_node(self):
        """Open URL configuration dialog"""
        dialog = UrlConfigDialog(self.url)
        if dialog.exec():
            new_url = dialog.get_url()
            if new_url != self.url:
                self.url = new_url
                self.update_tooltip()

    def update_tooltip(self):
        """Update node tooltip with current URL"""
        self.setToolTip(f"URL: {self.url}" if self.url else "URL not configured")

    def contextMenuEvent(self, event):
        """Handle right-click menu"""
        menu = QMenu()

        # Add standard actions
        configure_action = menu.addAction("Configure URL")
        menu.addSeparator()
        delete_action = menu.addAction("Delete Node")
        copy_action = menu.addAction("Copy Node")

        # Add URL-specific actions
        menu.addSeparator()
        if self.url:
            clear_action = menu.addAction("Clear URL")
            test_action = menu.addAction("Test URL")

        # Show menu and handle action
        action = menu.exec(event.screenPos())

        if action == configure_action:
            self.configure_node()
        elif action == delete_action:
            self.delete_node()
        elif action == copy_action:
            self.copy_node()
        elif self.url and action == clear_action:
            self.url = ""
            self.update_tooltip()
        elif self.url and action == test_action:
            self.test_url()

    def test_url(self):
        """Test if URL is accessible"""
        try:
            import requests
            response = requests.head(self.url)
            if response.status_code == 200:
                QMessageBox.information(None, "URL Test", "URL is accessible!")
            else:
                QMessageBox.warning(None, "URL Test", f"URL returned status code: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(None, "URL Test", f"Error testing URL: {str(e)}")

    def paint(self, painter, option, widget=None):
        """Custom paint to show URL status"""
        super().paint(painter, option, widget)

        # Draw URL preview if configured
        if self.url:
            painter.setPen(Qt.GlobalColor.white)
            url_text = self.url[:20] + "..." if len(self.url) > 20 else self.url
            painter.drawText(
                10,
                self.title_height + 20,
                self.width - 20,
                20,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                url_text
            )

    def serialize(self):
        """Convert node to JSON-compatible dictionary"""
        data = super().serialize()
        data['url'] = self.url
        return data

    def deserialize(self, data, hashmap={}):
        """Restore node from dictionary data"""
        super().deserialize(data, hashmap)
        self.url = data.get('url', "")
        self.update_tooltip()
        return True


class ScrollNode(Node):
    def __init__(self, scene):
        super().__init__(
            scene,
            title="Scroll",
            inputs=["Trigger"],
            outputs=["Next"]
        )
        self.scroll_amount = 300

    def do_execute(self):
        try:
            self.scene.browser.driver.execute_script(
                f"window.scrollBy(0, {self.scroll_amount});"
            )
            return True
        except Exception as e:
            self.scene.logger.error(f"Error scrolling: {str(e)}")
            return False

class LikePostNode(Node):
    def __init__(self, scene):
        super().__init__(
            scene,
            title="Like Post",
            inputs=["Trigger"],
            outputs=["Next"]
        )

    def do_execute(self):
        try:
            like_button = self.scene.browser.driver.find_element_by_xpath(
                "//span[contains(@class, 'like2')]"
            )
            like_button.click()
            return True
        except Exception as e:
            self.scene.logger.error(f"Error liking post: {str(e)}")
            return False