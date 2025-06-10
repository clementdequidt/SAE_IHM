#VUE_CLIENT

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QSlider ,   QCalendarWidget , QLineEdit , QPushButton, QHBoxLayout , QLabel ,QVBoxLayout, QTextEdit, QComboBox
from PyQt6.QtCore import Qt

class Test(QWidget):
    def __init__(self):

        super().__init__()

        self.resize(1920,1080)
        self.setWindowTitle('R2.02: Beaucoup de Widget ')
        layout = QHBoxLayout() ; self.setLayout(layout)
        
        self.combo: QComboBox = QComboBox()
        self.combo.addItems(['☐ produit1', '☐ produit2', '☐ produit3'])
        self.combo.activated.connect(self.caseCombo)
        layout.addWidget(self.combo)
        self.show()
        
    def caseCombo(self, indice) -> None:
        texte:str = self.combo.itemText(indice)
        if texte[0] == '☐':
            self.combo.setItemText(indice, '☑' + texte[1:])
        else:
            self.combo.setItemText(indice, '☐' + texte[1:])



if __name__ == '__main__':
    app = QApplication(sys.argv) 

    f = Test() 
    sys.exit(app.exec())