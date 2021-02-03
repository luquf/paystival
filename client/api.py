#!/usr/bin/env python3

from smartcard.System import readers
from config import *
from utils import *
from transaction import *
import hashlib
import struct
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
import sys, os, subprocess

CLA = 0xA0

"""
Instructions available on the card
"""
INS_VERIFY_PIN = 0x01
INS_DEBIT_BALANCE = 0x02
INS_CREDIT_BALANCE = 0x03
INS_REQUEST_BALANCE = 0x04
INS_REQUEST_INFO = 0x05
INS_REQUEST_TRANS = 0x06

P1 = 0x00	
P2 = 0x00
Le = 0x00 	


r = readers()
connection = r[0].createConnection()
connection.connect()

""" Data received from the card """
data = []
sw1 = 0x0
sw2 = 0x0

data, sw1, sw2 = connection.transmit(apdu)
if sw1 != 0x90 or sw2 != 0x0:
	print("An error occured with the card")
	exit(1)

# ENTER PIN
Le = 0x04
data, sw1, sw2 = connection.transmit([CLA,INS_VERIFY_PIN,P1,P2,Le]+[0x31, 0x32, 0x33, 0x34])
if sw1 == 0x98 and sw2 == 0x04:
	print("Wrong PIN")
else:
	print("Good PIN")

# GET BALANCE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	amount = data[0]
	amount = (amount << 8) | data[1]
	print(f"amount: {amount}€")
else:
	print("no operation 1")


# CREDIT BALANCE
Le = 0x2
data, sw1, sw2 = connection.transmit([CLA,INS_CREDIT_BALANCE,P1,P2,Le]+[0x00, 0x01])
if sw1 == 0x90 and sw2 == 0x00:
	print("credit done")
else:
	print("no operation 2")
	print_ret_codes(sw1, sw2)

# GET BALANCE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	amount = data[0]
	amount = (amount << 8) | data[1]
	print(f"amount: {amount}€")
else:
	print("no operation 3")


# DEBIT BALANCE
Le = 0x2
data, sw1, sw2 = connection.transmit([CLA,INS_DEBIT_BALANCE,P1,P2,Le]+[0x00, 0x02])
if sw1 == 0x90 and sw2 == 0x00:
	print("debit done")
else:
	print("no operation 4")


# GET BALANCE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	amount = data[0]
	amount = (amount << 8) | data[1]
	print(f"amount: {amount}€")
else:
	print("no operation 5")


# GET INFO
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_INFO,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	infos = parse_user_info(data)	
else:
	print("no operation 6")

# VERIFY THE INFORMATION SIGNATURE
with open("../keys/vk.pem") as f:
   vk = VerifyingKey.from_pem(f.read())

ok = vk.verify(bytearray(infos[3]), bytearray(infos[0]+infos[1]+infos[2]), hashlib.sha256, sigdecode=sigdecode_der)
assert ok

# REQUEST TRANS
for i in range(0, 1000):
	Le = 0x2
	data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_TRANS,P1,P2,Le]+[(i>>8)&0xFF, i&0xFF])
	if sw1 == 0x90 and sw2 == 0x00:
		t = Transaction(data)
		print(t)
		print("Verifying transaction =>", t.verify_transaction())
	else:
		break

connection.disconnect()

