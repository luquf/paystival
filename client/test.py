#!/usr/bin/env python3

from smartcard.System import readers
from config import *
from utils import *
from transaction import *
import hashlib
import struct
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from Crypto.PublicKey.RSA import construct
from sqlite3 import *
import sys, os, subprocess

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


# GET BALANCE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	amount = data[0]
	amount = (amount << 8) | data[1]
	print(f"amount: {amount}€")
else:
	print("no operation 1")

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

ok = vk.verify(bytearray(infos[3]), bytearray(infos[0]+infos[1]+infos[2]), hashlib.sha256)
assert ok



# COMPLETE CHALLENGE
enc = None
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_CHALLENGE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	conn = connect("../res/paystival.sqlite")	
	cur = conn.cursor()
	userid = to2hex(infos[2][0])+to2hex(infos[2][1])+to2hex(infos[2][2])+to2hex(infos[2][3])
	cur.execute("SELECT exponent, modulus FROM public_keys WHERE userid=?", (userid,))
	r = cur.fetchall()
	cur.close()
	conn.close()
	pubkey = construct((int(r[0][1], 10), r[0][0]))
	num = int.from_bytes(data, "big")
	enc = pubkey.encrypt(num, 0)[0]
	enc = list(enc.to_bytes(64, "big"))
else:
	print_ret_codes(sw1, sw2)
	print("no operation 8")


Le = 0x42
data, sw1, sw2 = connection.transmit([CLA,INS_CREDIT_BALANCE,P1,P2,Le]+[0x0, 0x02]+enc)
if sw1 == 0x90 and sw2 == 0x00:
	print("test credit done")
else:
	print_ret_codes(sw1, sw2)
	print("no operation 9")

# GET BALANCE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	amount = data[0]
	amount = (amount << 8) | data[1]
	print(f"amount: {amount}€")
else:
	print("no operation 1")


# COMPLETE CHALLENGE
enc = None
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_CHALLENGE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	conn = connect("../res/paystival.sqlite")	
	cur = conn.cursor()
	userid = to2hex(infos[2][0])+to2hex(infos[2][1])+to2hex(infos[2][2])+to2hex(infos[2][3])
	cur.execute("SELECT exponent, modulus FROM public_keys WHERE userid=?", (userid,))
	r = cur.fetchall()
	num = int.from_bytes(data, "big")
	cur.close()
	conn.close()
	pubkey = construct((int(r[0][1], 10), r[0][0]))
	enc = pubkey.encrypt(num, 0)[0]
	enc = list(enc.to_bytes(64, "big"))
else:
	print_ret_codes(sw1, sw2)
	print("no operation 8")


Le = 0x42
data, sw1, sw2 = connection.transmit([CLA,INS_DEBIT_BALANCE,P1,P2,Le]+[0x0, 0x02]+enc)
if sw1 == 0x90 and sw2 == 0x00:
	print("test debit done")
else:
	print_ret_codes(sw1, sw2)
	print("no operation 9")

# GET BALANCE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	amount = data[0]
	amount = (amount << 8) | data[1]
	print(f"amount: {amount}€")
else:
	print("no operation 1")

connection.disconnect()

