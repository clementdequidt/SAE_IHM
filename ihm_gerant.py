import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget
)
from PyQt6.QtCore import Qt

class FenetrePrincipale(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("app:layout")
        self.resize(QApplication.primaryScreen().availableGeometry().size())
        self.move(0, 0)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fen = FenetrePrincipale()
    sys.exit(app.exec())
