from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from api import *
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from utils import *
from config import *
from sqlite3 import *
import sys, os, subprocess
import time
import hashlib


class MainWindow(QMainWindow):

	def __init__(self, *args, **kwargs):

		super(MainWindow, self).__init__(*args, **kwargs)

		self.pin_validated = False
		self.setWindowTitle("Paystival cash register")
		self.setGeometry(200,200,1200,800)
		self.calc_view()
		self.connection = create_connection()

	def check_con(self):
		ok = is_card_connected()
		if ok:
			self.connection = create_connection()
		return ok

	def no_card_popup(self):
		self.dialog = QDialog()
		self.dialog.resize(300, 100)
		tdiag = QLabel("Veuillez brancher une carte !", self.dialog)
		tdiag.move(50, 20)
		bdiag = QPushButton("Retour", self.dialog)
		bdiag.clicked.connect(self.dialog.done)
		bdiag.move(115, 60)
		self.dialog.setWindowTitle("Aucune carte détectée")
		self.dialog.setWindowModality(Qt.ApplicationModal)
		self.dialog.exec_()

	def calc_view(self):
		self.main_widget = CalcViewWidget(self)
		self.setCentralWidget(self.main_widget)

class CalcViewWidget(QWidget):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent

		# Initialize the PIN field
		self.amount = ""

		# Construction the PIN widget
		self.amountfield = QWidget()
		self.labelfield = QLabel("Montant:")
		self.labelfield.setAlignment(Qt.AlignCenter)
		font = self.labelfield.font();
		font.setPointSize(40);
		self.labelfield.setFont(font);
		self.layout = QGridLayout()
		self.amountlayout = QGridLayout()
		self.buttons = [[QPushButton("1"), QPushButton("2"), QPushButton("3")],
						[QPushButton("4"), QPushButton("5"), QPushButton("6")],
						[QPushButton("7"), QPushButton("8"), QPushButton("9")],
						[QPushButton("X"), QPushButton("0"), QPushButton("V")]]
		for i in range(4):
			for j in range(3):
				self.buttons[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
				font = self.buttons[i][j].font();
				font.setPointSize(20);
				self.buttons[i][j].setFont(font);
				if not (i == 4 and j == 2) and not (i == 4 and j == 0):
					self.buttons[i][j].clicked.connect(self.button_clicked)
				self.amountlayout.addWidget(self.buttons[i][j], i, j)
		self.layout.addWidget(self.labelfield, 0, 0)
		self.layout.setContentsMargins(50, 50, 50, 50)
		self.amountfield.setLayout(self.amountlayout)
		self.layout.addWidget(self.amountfield, 1, 0)
		self.setLayout(self.layout)
	
	def update_field(self, val):
		self.labelfield.setText(val)

	def button_clicked(self):
		num = "0123456789" 
		actions = "VX"
		b = self.sender().text()
		if b in num:
				self.amount += str(b)
				self.update_field("Montant: "+self.amount)
		elif b in actions:
			if b == "V":
				if is_card_connected():
					try:
						close_connection(self.parent.connection)
						self.parent.connection = create_connection()
					except:
						pass
					self.nextv = DebitViewWidget(self.parent, self.amount)
					self.parent.setCentralWidget(self.nextv)
					self.parent.connection = create_connection()
					self.parent.subwindow = PINViewWidget(self.parent)
					self.parent.subwindow.exec_()
					if self.parent.pin_validated:
						ok = debit_balance(self.parent.connection, int(self.amount, 10))
						if ok:
							self.nextv.update_status("Transaction terminée!", "green")
						else:
							self.nextv.update_status("Echec de la transaction", "red")
					self.parent.pin_validated = False
					try:
						close_connection(self.parent.connection)
					except:
						pass
				else:
					self.dialog = QDialog()
					self.dialog.resize(300, 100)
					tdiag = QLabel("Veuillez brancher une carte !", self.dialog)
					tdiag.move(50, 20)
					bdiag = QPushButton("Retour", self.dialog)
					bdiag.clicked.connect(self.dialog.done)
					bdiag.move(115, 60)
					self.dialog.setWindowTitle("Aucune carte détectée")
					self.dialog.setWindowModality(Qt.ApplicationModal)
					self.dialog.exec_()
			elif b == "X":
				self.amount = ""
				self.update_field("Montant: ")

class DebitViewWidget(QWidget):

	def __init__(self, parent, amount):
		super().__init__()
		self.parent = parent
		self.amount = amount
		
		self.layout = QGridLayout()
		self.text = QLabel(f"Transaction de {self.amount}€")
		self.status = QLabel(f"Statut: en attente de paiement")
		self.status.setStyleSheet("color: orange") 
		self.button  =QPushButton("Retour")
		self.text.setFont(QFont("Arial", 40))
		self.status.setFont(QFont("Arial", 40))
		self.button.setFont(QFont("Arial", 30))
		self.button.clicked.connect(self.button_clicked)
		self.text.setAlignment(Qt.AlignCenter)
		self.status.setAlignment(Qt.AlignCenter)
		self.layout.addWidget(self.text, 0, 0)
		self.layout.addWidget(self.status, 1, 0)
		self.layout.addWidget(self.button, 2, 0)
		self.setLayout(self.layout)
		
	def update_status(self, text, color):
		self.status.setText(text)
		self.status.setStyleSheet(f"color: {color}") 

	def button_clicked(self):
		self.parent.subwindow.done(0)
		self.parent.pin_validated = False
		self.parent.calc_view()


class PINViewWidget(QDialog):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent

		# Initialize the PIN field
		self.pin = ""
		
		# Construction the PIN widget
		self.pinfield = QWidget()
		self.labelfield = QLabel("Entrez votre PIN")
		self.labelfield.setAlignment(Qt.AlignCenter)
		font = self.labelfield.font();
		font.setPointSize(40);
		self.labelfield.setFont(font);
		self.layout = QGridLayout()
		self.pinlayout = QGridLayout()
		self.buttons = [[QPushButton("1"), QPushButton("2"), QPushButton("3")],
						[QPushButton("4"), QPushButton("5"), QPushButton("6")],
						[QPushButton("7"), QPushButton("8"), QPushButton("9")],
						[QPushButton("X"), QPushButton("0"), QPushButton("V")],
						[QWidget(), QPushButton("Retour"), QWidget()]]
		for i in range(5):
			for j in range(3):
				self.buttons[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
				font = self.buttons[i][j].font();
				font.setPointSize(20);
				self.buttons[i][j].setFont(font);
				if not (i == 4 and j == 2) and not (i == 4 and j == 0):
					self.buttons[i][j].clicked.connect(self.button_clicked)
				self.pinlayout.addWidget(self.buttons[i][j], i, j)
		self.layout.addWidget(self.labelfield, 0, 0)
		self.layout.setContentsMargins(50, 50, 50, 50)
		self.pinfield.setLayout(self.pinlayout)
		self.layout.addWidget(self.pinfield, 1, 0)
		self.setLayout(self.layout)
	
	def update_field(self, val):
		self.labelfield.setText(val)

	def button_clicked(self):
		num = "0123456789" 
		actions = "VX"
		b = self.sender().text()
		if b in num:
			if len(self.pin) < 4:
				self.pin += b
				self.update_field("PIN: "+"*"*len(self.pin))
		elif b in actions:
			if b == "V":
				self.validate_pin()
			elif b == "X":
				self.pin = self.pin[:len(self.pin)-1]
				if self.pin != "":
					self.update_field("PIN: "+"*"*len(self.pin))
				else:
					self.update_field("Entrez votre PIN")
		else:
			self.parent.subwindow.done(0)
			self.parent.pin_validated = False
			self.parent.calc_view()

	def validate_pin(self):
		close_connection(self.parent.connection)
		self.parent.connection = create_connection()
		# Call the API to validate the pin
		ok = ask_pin_validation(self.parent.connection, [ord(c) for c in self.pin])
		if ok:
			self.parent.pin_validated = True
			self.close()
		else:
			self.update_field("Le PIN entré est invalide")
			self.pin = ""


