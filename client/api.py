#!/usr/bin/env python3

from smartcard.System import readers
from config import *
import sys, os, subprocess

def to_2hex(val):
	fmt = "%0.2x" % val
	return fmt.format(val)


CLA = 0xA0
INS_VERIFY_PIN = 0x01
INS_DEBIT_BALANCE = 0x02
INS_CREDIT_BALANCE = 0x03
INS_REQUEST_BALANCE = 0x04
P1 = 0x00	
P2 = 0x00
Le = 0x00 	# Set to 0 means the client does not know the size of received data 

if len(sys.argv) < 2:
	print("usage: python3 wallet_backend.py <register> or <process>")
	exit()

arg = sys.argv[1]

if arg == "register":
	out = subprocess.Popen(['java', '-jar', GP_PATH, '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	out = str(out.stdout.read())
	if AID_STR in out:
		print("An account has already been set on this card... exiting")
		exit()
	else:
		first_name = input("First name: ")
		last_name = input("Last name: ")
		pin = input("PIN (4 chiffres): ")
		amount = input("Amount of money (1-500€): ")
		hex_pin = "".join([to_2hex(ord('0')+int(val)) for val in pin])
		out = subprocess.Popen(['java', '-jar', GP_PATH, '-install', BIN_PATH, '-default', '-params', hex_pin], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		print("Your card has been configured")

elif arg == "process":
	r = readers()
	connection = r[0].createConnection()
	connection.connect()
	
	data, sw1, sw2 = connection.transmit(apdu)
	if sw1 != 0x90 or sw2 != 0x0:
		print("An error occured with the card")
		exit(1)
	
	
	sw1 = 0x0
	sw2 = 0x0
	while sw1 != 0x90 or sw2 != 0x0:
		pin = input("Enter your pin: ")
		pin = [ord(c) for c in pin]
		if len(pin) != 4:
			print("The PIN must be 4 numbers")
			continue
		Le = len(pin)
		data, sw1, sw2 = connection.transmit([CLA,INS_VERIFY_PIN,P1,P2,Le]+pin)
		if sw1 == 0x98 and sw2 == 0x04:
			print("Wrong PIN")
	
	
	
	command = ""
	
	while command != "q":
		print("1. Register my card")
		print("2. Add money on my card")
		print("3. See my balance")
		print("4. Transfer money to another card")
		
		command = input("Enter your choice: ")
	
		if command == "1":
			pass
		elif command == "2":
			pass
		elif command == "3":
			pass
		elif command == "4":
			pass
		else:
			print("Please enter a valid command")
	
	
	# Disconnect the reader
	connection.disconnect()
else:
	print("Unkown command")
	exit()
	


