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
import hashlib


class MainWindow(QMainWindow):

	def __init__(self, *args, **kwargs):

		super(MainWindow, self).__init__(*args, **kwargs)

		self.setWindowTitle("Paystival")
		self.setGeometry(200,200,1200,800)
		self.button_view()
		self.connection = create_connection()

	def check_con(self):
		ok = is_card_connected()
		if ok:
			self.connection = create_register_connection()
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

	def button_view(self):
		self.main_widget = ButtonViewWidget(self)
		self.setCentralWidget(self.main_widget)

	def pin_view(self, nextv):
		if not self.check_con():
			self.no_card_popup()
		else:
			self.main_widget = PINViewWidget(self, nextv)
			self.setCentralWidget(self.main_widget)
	
	def balance_view(self, amount):
		if not self.check_con():
			self.no_card_popup()
		else:
			self.main_widget = BalanceViewWidget(self, amount)
			self.setCentralWidget(self.main_widget)

	def register_view(self):
		if not self.check_con():
			self.no_card_popup()
		else:
			self.main_widget = RegisterViewWidget(self)
			self.setCentralWidget(self.main_widget)

	def charge_view(self, conn):
		if not self.check_con():
			self.no_card_popup()
		else:
			self.main_widget = ChargeViewWidget(self, conn)
			self.setCentralWidget(self.main_widget)

	def transfer_view(self, trans):
		if not self.check_con():
			self.no_card_popup()
		else:
			self.main_widget = TransferViewWidget(self, trans)
			self.setCentralWidget(self.main_widget)

	def transfer_option(self):
		self.pin_view("transfer")

	def charge_option(self):
		self.pin_view("charge")

	def balance_option(self):
		self.pin_view("balance")



class TransferViewWidget(QWidget):

	def __init__(self, parent, trans):
		super().__init__()
		self.parent = parent

		# Construction du widget
		self.glayout = QGridLayout()
		self.tablewidget = QTableWidget(len(trans), 6)
		self.tablewidget.horizontalHeader().setStretchLastSection(True) 
		self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
		self.tablewidget.setHorizontalHeaderLabels(['Montant','Type', 'ID', 'Origine', 'Destination', 'Signature vérifiée'])
		for i in range(len(trans)):
			item = QTableWidgetItem(str(trans[i].amount)+'€')
			item.setTextAlignment(Qt.AlignHCenter)
			self.tablewidget.setItem(i, 0, item) 
			item = QTableWidgetItem(trans[i].trans_type[trans[i].type])
			item.setTextAlignment(Qt.AlignHCenter)
			self.tablewidget.setItem(i, 1, item) 
			item = QTableWidgetItem(to8hex(trans[i].tid))
			item.setTextAlignment(Qt.AlignHCenter)
			self.tablewidget.setItem(i, 2, item) 
			item = QTableWidgetItem("Utilisateur" if not trans[i].from_ else to8hex(trans[i].from_))
			item.setTextAlignment(Qt.AlignHCenter)
			self.tablewidget.setItem(i, 3, item) 
			item = QTableWidgetItem("Festival" if trans[i].to==0xFFFFFFFF else to8hex(trans[i].to))
			item.setTextAlignment(Qt.AlignHCenter)
			self.tablewidget.setItem(i, 4, item) 
			item = QTableWidgetItem("Oui" if trans[i].verify_transaction() else "Non")
			item.setTextAlignment(Qt.AlignHCenter)
			self.tablewidget.setItem(i, 5, item) 

		self.back = QPushButton("Retour")
		self.back.setFont(QFont("Arial", 20))
		self.back.clicked.connect(self.button_clicked)
		self.glayout.addWidget(self.tablewidget, 0, 0)
		self.glayout.addWidget(self.back, 1, 0)
		self.setLayout(self.glayout)

	def button_clicked(self):
		self.parent.button_view()	


class ChargeViewWidget(QWidget):

	def __init__(self, parent, connection):
		super().__init__()
		self.parent = parent
		self.conn = connection

		# Construction du widget
		self.flayout = QFormLayout()
		self.flayout.setContentsMargins(50, 50, 50, 50)
		self.amount = QLabel("Montant")
		self.amount.setFont(QFont("Arial", 20))
		self.amountfield = QLineEdit()	
		self.amountfield.setFixedHeight(50)
		self.amountfield.setFont(QFont("Arial", 20))
		self.buttons = [QPushButton("Retour"), QPushButton("Valider")]
		self.buttons[0].clicked.connect(self.button_clicked)
		self.buttons[1].clicked.connect(self.button_clicked)
		self.buttons[0].setFont(QFont("Arial", 20))
		self.buttons[1].setFont(QFont("Arial", 20))
		self.flayout.addRow(self.amount, self.amountfield)
		self.flayout.addRow(QLabel(""), QLabel(""))
		self.flayout.addRow(self.buttons[0], self.buttons[1])
		self.setLayout(self.flayout)

	def button_clicked(self):
		text = self.sender().text()
		if text == "Retour":
			self.parent.button_view()
		elif text == "Valider":
			try:
				a = int(self.amountfield.text(), 10)
				# API call to credit the card	
				ok = credit_balance(self.parent.connection, a)
				if ok:
					self.dialog = QDialog()
					self.dialog.resize(300, 100)
					tdiag = QLabel("Rechargement terminé !", self.dialog)
					tdiag.move(50, 20)
					bdiag = QPushButton("Retour", self.dialog)
					bdiag.clicked.connect(self.home_clicked)
					bdiag.move(115, 60)
					self.dialog.setWindowTitle("Opération réussie")
					self.dialog.setWindowModality(Qt.ApplicationModal)
					self.dialog.exec_()
				else:
					self.dialog = QDialog()
					self.dialog.resize(300, 100)
					tdiag = QLabel("Echec du rechargement !", self.dialog)
					tdiag.move(50, 20)
					bdiag = QPushButton("Retour", self.dialog)
					bdiag.clicked.connect(self.home_clicked)
					bdiag.move(115, 60)
					self.dialog.setWindowTitle("Echec de l'opération")
					self.dialog.setWindowModality(Qt.ApplicationModal)
					self.dialog.exec_()

			except Exception as e:
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("Mauvais montant !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Echec du rechargement")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()

	def home_clicked(self):
		self.dialog.done(0)
		self.parent.button_view()

class RegisterViewWidget(QWidget):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent

		# Construction du widget
		self.buttons = [QPushButton("Valider"), QPushButton("Retour")]
		self.buttons[0].setFont(QFont("Arial", 20))
		self.buttons[0].clicked.connect(self.button_clicked)
		self.buttons[1].setFont(QFont("Arial", 20))
		self.buttons[1].clicked.connect(self.button_clicked)
		self.first_name = QLabel("Prénom  ")
		self.first_name.setFont(QFont("Arial", 20))
		self.last_name = QLabel("Nom  ")
		self.last_name.setFont(QFont("Arial", 20))
		self.userid = QLabel("ID  ")
		self.userid.setFont(QFont("Arial", 20))
		self.pin = QLabel("PIN  ")
		self.pin.setFont(QFont("Arial", 20))

		self.first_namefield = QLineEdit()
		self.first_namefield.setFixedHeight(50)
		self.first_namefield.setFont(QFont("arial", 20))
		self.last_namefield = QLineEdit()
		self.last_namefield.setFixedHeight(50)
		self.last_namefield.setFont(QFont("Arial", 20))
		self.useridfield = QLineEdit()
		self.useridfield.setFixedHeight(50)
		self.useridfield.setFont(QFont("Arial", 20))
		self.pin1field = QLineEdit()
		self.pin1field.setEchoMode(QLineEdit.Password)
		self.pin1field.setFixedHeight(50)
		self.pin1field.setFont(QFont("Arial", 20))
		self.pin2field = QLineEdit()
		self.pin2field.setEchoMode(QLineEdit.Password)
		self.pin2field.setFixedHeight(50)
		self.pin2field.setFont(QFont("Arial", 20))

		self.flayout = QFormLayout()
		self.flayout.setContentsMargins(50, 50, 50, 50)
		self.flayout.addRow(self.first_name, self.first_namefield)
		self.flayout.addRow(QLabel(""), QLabel(""))
		self.flayout.addRow(self.last_name, self.last_namefield)
		self.flayout.addRow(QLabel(""), QLabel(""))
		self.flayout.addRow(self.userid, self.useridfield)
		self.flayout.addRow(QLabel(""), QLabel(""))
		self.vbox = QVBoxLayout()
		self.vbox.addWidget(self.pin1field)
		self.vbox.addWidget(self.pin2field)
		self.flayout.addRow(self.pin, self.vbox)
		self.flayout.addRow(QLabel(""), QLabel(""))
		self.flayout.addRow(self.buttons[1], self.buttons[0])
		self.setLayout(self.flayout)

	def button_clicked(self):
		b = self.sender().text()
		if b == "Retour":
			self.parent.button_view()
		elif b == "Valider":
			self.buttons[0].setEnabled(False)
			self.buttons[1].setEnabled(False)
			self.buttons[0].setText("Chargement...")
			fn = self.first_namefield.text()
			ln = self.last_namefield.text()
			uid = self.useridfield.text()
			p1 = self.pin1field.text()
			p2 = self.pin2field.text()
			if fn == "":
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("Prénom invalide !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Echec de l'enregistrement")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()
			elif ln == "":
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("Nom invalide !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Echec de l'enregistrement")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()

			elif len(uid) != 8:
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("ID client invalide !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Echec de l'enregistrement")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()

			elif p1 != p2 or len(p1) != 4:
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("PINs invalides ou différents !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Echec de l'enregistrement")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()

			else:
				with open("../keys/sk.pem") as f:
				   sk = SigningKey.from_pem(f.read(), hashlib.sha256)
			
				try:
					close_connection(self.parent.connection)	
				except:
					pass
				first_name = pad_array([ord(c) for c in fn], 0x14)
				last_name = pad_array([ord(c) for c in ln], 0x14)
				data = first_name + last_name + hex_to_array(uid)
				new_signature = sk.sign_deterministic(bytearray(data))
				hsig = new_signature.hex()
				first_name = array_to_hexdigest(first_name)
				last_name = array_to_hexdigest(last_name)
				pin = str2hex(p1)
				param = pin + first_name + last_name + uid + hsig
				param = param.upper()
				out = subprocess.Popen(['java', '-jar', GP_PATH, '-delete', '0102030405'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				out.stdout.read()
				out = subprocess.Popen(['java', '-jar', GP_PATH, '-install', BIN_PATH, '-default', '-params', param], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				out.stdout.read()

				self.parent.connection = create_connection()
				ok = ask_and_store_public_key(self.parent.connection, uid)
				
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("Enregistrement effectué avec succès !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Enregistrement effectué")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()
		
	def home_clicked(self):
		self.dialog.done(0)
		self.parent.button_view()


class BalanceViewWidget(QWidget):

	def __init__(self, parent, amount):
		super().__init__()
		self.parent = parent
		self.amount = amount

		self.layout = QGridLayout()
		self.amountfield = QLabel(f"Votre balance est: {self.amount}€")
		self.amountfield.setAlignment(Qt.AlignCenter)
		font = self.amountfield.font();
		font.setPointSize(40);
		self.amountfield.setFont(font);
		self.backbutton = QPushButton("Retour au menu")
		self.backbutton.clicked.connect(self.button_clicked)
		font = self.backbutton.font();
		font.setPointSize(30);
		self.backbutton.setFont(font);
		self.layout.addWidget(self.amountfield, 0, 0)
		self.layout.addWidget(self.backbutton, 1, 0)
		self.setLayout(self.layout)
	
	def button_clicked(self):
		self.parent.button_view()


class ButtonViewWidget(QWidget):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		
		# Construct the widget
		self.layout = QGridLayout()
		self.buttons = [[QPushButton(" Enregistrer ma carte"), QPushButton(" Recharger ma carte")], 
					    [QPushButton(" Historique de transactions"), QPushButton(" Voir ma balance")]]
		self.actions = [[self.parent.register_view, self.parent.charge_option], [self.parent.transfer_option, self.parent.balance_option]]
		for i in range(2):
			for j in range(2):
				self.buttons[i][j].setGeometry(QRect(1000, 1000, 93, 28))
				self.buttons[i][j].setIcon(QIcon("icons/"+str(i)+str(j)+".png"))
				self.buttons[i][j].setIconSize(QSize(48, 48))
				self.buttons[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
				font = self.buttons[i][j].font();
				font.setPointSize(20);
				self.buttons[i][j].setFont(font);
				self.buttons[i][j].clicked.connect(self.actions[i][j])
				self.layout.addWidget(self.buttons[i][j], i, j)
		self.setLayout(self.layout)


class PINViewWidget(QWidget):

	def __init__(self, parent, nextv):
		super().__init__()
		self.parent = parent
		self.nextv = nextv

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
		elif b == "Retour":
			self.parent.button_view()

	def validate_pin(self):
		close_connection(self.parent.connection)
		self.parent.connection = create_connection()
		# Call the API to validate the pin
		ok = ask_pin_validation(self.parent.connection, [ord(c) for c in self.pin])
		if ok:
			if self.nextv == "balance":
				# Call backend API to get the balance
				amount = ask_balance(self.parent.connection)
				self.parent.balance_view(amount)
			elif self.nextv == "charge":
				self.parent.charge_view(self.parent.connection)
			elif self.nextv == "transfer":
				trans = get_transaction_history(self.parent.connection)
				self.parent.transfer_view(trans)
		else:
			self.update_field("Le PIN entré est invalide")
			self.pin = ""



