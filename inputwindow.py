import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import consentform

class InputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Consent Form Generator')
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel('Consent Form PDF Generator')
        header.setFont(QFont('Arial', 20))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Input layout
        input_layout = QHBoxLayout()
        entry_label = QLabel('Number of Pets: ')
        self.input_box = QLineEdit()
        
        input_layout.addWidget(entry_label)
        input_layout.addWidget(self.input_box)
        
        main_layout.addLayout(input_layout)
        
        # Submit button
        self.submit_button = QPushButton('Generate')
        self.submit_button.clicked.connect(self.submitNumber)
        main_layout.addWidget(self.submit_button)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Set window size
        self.resize(400, 200)
        
        # Bind Enter key to submitNumber function
        self.input_box.returnPressed.connect(self.submitNumber)
        
        self.show()
    
    def submitNumber(self):
        pdf_file = os.path.join(os.path.expanduser("~"), "Desktop/", 'ConsentForm.pdf')  # sets the file location to the desktop
        try:
            numberOfPets = int(self.input_box.text())  # gets the number of pets from the entry box
        except ValueError:
            QMessageBox.critical(self, 'Invalid Value', 'Please enter a number')  # shows error if the entered value is invalid
            return
        
        consentform.ConsentForm(pdf_file).drawConsentForm(numberOfPets=numberOfPets)  # creates the pdf
        QMessageBox.information(self, 'PDF Created!', 'You will find the PDF on your desktop')  # shows message when the pdf is made 
        self.close()  # gets rid of the window

# Run the application
def setUpGui():
    app = QApplication(sys.argv)
    window = InputWindow()
    sys.exit(app.exec())

