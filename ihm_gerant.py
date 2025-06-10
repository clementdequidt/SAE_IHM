import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget
)
from PyQt6.QtCore import Qt

class FenetrePrincipale(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("app:layout")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fen = FenetrePrincipale()
    sys.exit(app.exec())
