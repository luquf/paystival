from gui import MainWindow
from PyQt5.QtWidgets import *
from sys import argv

if __name__=="__main__":
	app = QApplication(argv)
	
	window = MainWindow()
	window.show()
	
	app.exec_()
