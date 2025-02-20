from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QLabel)
from PyQt6.QtCore import Qt


class ProfileSelectorDialog(QDialog):
    def __init__(self, profiles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Profile")
        self.profiles = profiles
        self.selected_profile = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Profile selector
        selector_layout = QHBoxLayout()
        label = QLabel("Profile:")
        self.profile_combo = QComboBox()

        # Add profiles to combo box
        for profile_name in self.profiles:
            self.profile_combo.addItem(profile_name)

        selector_layout.addWidget(label)
        selector_layout.addWidget(self.profile_combo)
        layout.addLayout(selector_layout)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
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
            QComboBox {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
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
        """)

    def get_selected_profile(self):
        return self.profile_combo.currentText()