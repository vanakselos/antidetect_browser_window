from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton)
from PyQt6.QtCore import Qt


class CreateProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Create New Profile')
        self.setModal(True)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        # Profile name input
        name_layout = QHBoxLayout()
        name_label = QLabel('Profile Name:')
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton('Create')
        cancel_button = QPushButton('Cancel')

        create_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton[text="Cancel"] {
                background-color: #6c757d;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #5a6268;
            }
        """)

    def get_profile_name(self) -> str:
        return self.name_input.text().strip()