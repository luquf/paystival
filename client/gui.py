import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from api import *


class MainWindow(QMainWindow):

	def __init__(self, *args, **kwargs):

		super(MainWindow, self).__init__(*args, **kwargs)

		self.setWindowTitle("Paystival")
		self.setGeometry(200,200,1200,800)
		self.button_view()

	def button_view(self):
		self.main_widget = ButtonViewWidget(self)
		self.setCentralWidget(self.main_widget)

	def pin_view(self, nextv):
		self.main_widget = PINViewWidget(self, nextv)
		self.setCentralWidget(self.main_widget)
	
	def balance_view(self, amount):
		self.main_widget = BalanceViewWidget(self, amount)
		self.setCentralWidget(self.main_widget)

	def register_view(self):
		self.main_widget = RegisterViewWidget(self)
		self.setCentralWidget(self.main_widget)

	def charge_view(self):
		self.main_widget = ChargeViewWidget(self)
		self.setCentralWidget(self.main_widget)

	def transfer_option(self):
		pass

	def charge_option(self):
		self.pin_view("charge")

	def balance_option(self):
		self.pin_view("balance")

class ChargeViewWidget(QWidget):

	def _init__(self, parent):
		super().__init__()
		self.parent = parent

		# Construction du widget
		self.layout = QFormLayout()
		self.amount = QLabel("Amount")
		self.amountfield = QLineEdit()	
		self.setLayout(self.layout)

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
		self.amount = QLabel("Montant  ")
		self.amount.setFont(QFont("Arial", 20))
		self.pin = QLabel("PIN  ")
		self.pin.setFont(QFont("Arial", 20))

		self.first_namefield = QLineEdit()
		self.first_namefield.setFixedHeight(50)
		self.first_namefield.setFont(QFont("Arial", 20))
		self.last_namefield = QLineEdit()
		self.last_namefield.setFixedHeight(50)
		self.last_namefield.setFont(QFont("Arial", 20))
		self.useridfield = QLineEdit()
		self.useridfield.setFixedHeight(50)
		self.useridfield.setFont(QFont("Arial", 20))
		self.amountfield = QLineEdit()
		self.amountfield.setFixedHeight(50)
		self.amountfield.setFont(QFont("Arial", 20))
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
		self.flayout.addRow(self.amount, self.amountfield)
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
			fn = self.first_namefield.text()
			ln = self.last_namefield.text()
			uid = self.useridfield.text()
			a = self.amountfield.text()
			p1 = self.pin1field.text()
			p2 = self.pin2field.text()
			try:
				a = int(a, 10)	
			except:
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("Montant invalide !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Echec de l'enregistrement")
				self.dialog.setWindowModality(Qt.ApplicationModal)
				self.dialog.exec_()
				return
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

			elif len(uid) != 16:
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("ID client invalide !", self.dialog)

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

			# TODO: api call to write data on the card + sign and stuff
			else:
				self.dialog = QDialog()
				self.dialog.resize(300, 100)
				tdiag = QLabel("Transaction effectuée avec succès !", self.dialog)
				tdiag.move(50, 20)
				bdiag = QPushButton("Retour", self.dialog)
				bdiag.clicked.connect(self.home_clicked)
				bdiag.move(115, 60)
				self.dialog.setWindowTitle("Transaction effectuée")
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
					    [QPushButton(" Transfert vers une autre carte"), QPushButton(" Voir ma balance")]]
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
		# Call backend API to validate the PIN
		amount = ask_balance_with_pin([ord(c) for c in self.pin])
		if amount != -1:
			if self.nextv == "balance":
				self.parent.balance_view(amount)
			elif self.nextv == "charge":
				self.parent.charge_view()
		else:
			self.update_field("Le PIN entré est invalide")
			self.pin = ""



