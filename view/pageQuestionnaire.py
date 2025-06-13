from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class PageQuestionnaire(QWidget):
    questionnaireValide = pyqtSignal(dict)
    
    def __init__(self, switchCallback):
        super().__init__()
        self.switchCallback = switchCallback

        formLayout = QVBoxLayout() #layout vertical pour structurer le questionnaire
        formLayout.setContentsMargins(40, 40, 40, 40)
        formLayout.setSpacing(15) #Espacement de 15 entre chaque layout

        title = QLabel("Création d'un nouveau magasin") #Label pour préciser ce que l'on fais
        title.setStyleSheet("font-size: 24px; font-weight: bold;") #Police utilisé, caractère, taille et mise en gras
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formLayout.addWidget(title)

        self.projetInput = self.ajouterLabelInput("Nom du projet :", "Saisissez le nom du projet", formLayout) #Ajout d'un label pour saisir le nom du projet
        self.auteurInput = self.ajouterLabelInput("Votre nom  :", "Saisissez votre nom", formLayout) #Ajout d'un label pour saisir notre nom 
        self.dateInput = self.ajouterDateInput("Date de création :", formLayout) #Ajout d'un label pour saisir la date de création

        self.nomMagasinInput = self.ajouterLabelInput("Nom du magasin :", "Nom du magasin", formLayout)  #Ajout d'un label pour saisir le nom du magasin
        self.adresseMagasinInput = self.ajouterLabelInput("Adresse du magasin :", "Adresse complète", formLayout) #Ajout d'un label pour saisir l'adresse du magasin

        btnValider = QPushButton("Valider") #Un bouton pour valider
        btnValider.clicked.connect(self.verifierEtPasser)#Appel d'une fonction, si tout les champs
        #sont complé alors on peut passer sinon on ne peut pas valider
        formLayout.addWidget(btnValider)

        outerLayout = QVBoxLayout() #Ajout d'un layout vertical
        outerLayout.addStretch()
        outerLayout.addLayout(formLayout)
        outerLayout.addStretch()
        self.setLayout(outerLayout)

        #On définit la taille de police des label, des lineEdit,DateEdit et des Bouttons
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit {
                border: 1px solid;
                border-radius: 5px;
                margin-bottom: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

    def ajouterLabelInput(self, labelText, placeholder, layout):
        layout.addWidget(QLabel(labelText))
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        layout.addWidget(line)
        return line

    def ajouterDateInput(self, labelText, layout):
        layout.addWidget(QLabel(labelText))
        dateEdit = QDateEdit()
        dateEdit.setCalendarPopup(True)
        dateEdit.setDate(QDate.currentDate())
        layout.addWidget(dateEdit)
        return dateEdit

    #Si tout les champs ne sont pas vérifier et rempli alors on renvoie un warning pour dire que les champs sont nécessaires
    def verifierEtPasser(self):
        if not all([
            self.projetInput.text().strip(),
            self.auteurInput.text().strip(),
            self.nomMagasinInput.text().strip(),
            self.adresseMagasinInput.text().strip()
        ]):
            QMessageBox.warning(self, "Champs requis", "Veuillez remplir tous les champs.")
            return
        self.questionnaireValide.emit(self.getQuestionnaireData())
        self.switchCallback()


    def getQuestionnaireData(self):
        return {
            "nom_projet": self.projetInput.text().strip(),
            "auteur": self.auteurInput.text().strip(),
            "date_creation": self.dateInput.date().toString(Qt.DateFormat.ISODate),
            "nom_magasin": self.nomMagasinInput.text().strip(),
            "adresse_magasin": self.adresseMagasinInput.text().strip()
        }