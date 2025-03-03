class Styles:
    MAIN_WINDOW = """
        QMainWindow {
            background-color: #f5f5f5;
        }
    """

    PROFILE_CARD = """
        QFrame {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
        }
    """

    BUTTONS = """
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
        QPushButton:disabled {
            background-color: #cccccc;
        }
    """

    INPUT_FIELDS = """
        QLineEdit {
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QLineEdit:focus {
            border: 1px solid #007bff;
        }
    """

    @classmethod
    def get_all_styles(cls):
        return f"""
            {cls.MAIN_WINDOW}
            {cls.PROFILE_CARD}
            {cls.BUTTONS}
            {cls.INPUT_FIELDS}
        """