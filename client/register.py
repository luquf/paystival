#!/usr/bin/env python3

from smartcard.System import readers
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from utils import *
from config import *
from sqlite3 import *
import sys, os, subprocess
import hashlib


first_name = input("First name: ")
last_name = input("Last name: ")
userid = input("User ID: ")
pin = input("PIN (4 chiffres): ")

# CARD CREATION PROCESS
with open("../keys/sk.pem") as f:
   sk = SigningKey.from_pem(f.read(), hashlib.sha256)

first_name = pad_array([ord(c) for c in first_name], 0x14)
last_name = pad_array([ord(c) for c in last_name], 0x14)

data = first_name + last_name + hex_to_array(userid)
new_signature = sk.sign_deterministic(bytearray(data))
hsig = new_signature.hex()

first_name = array_to_hexdigest(first_name)
last_name = array_to_hexdigest(last_name)
pin = str2hex(pin)

param = pin + first_name + last_name + userid + hsig
param = param.upper()


out = subprocess.Popen(['java', '-jar', GP_PATH, '-delete', '0102030405'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out.stdout.read()
out = subprocess.Popen(['java', '-jar', GP_PATH, '-install', BIN_PATH, '-default', '-params', param], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out.stdout.read()

r = readers()
connection = r[0].createConnection()
connection.connect()

# GET PUBLIC KEY AND STORE IT IN DATABASE
Le = 0x0
data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_PUB_KEY,P1,P2,Le])
if sw1 == 0x90 and sw2 == 0x00:
	pkey = get_card_public_key(data)
	conn = connect("../storage/pk_infra.sqlite")
	cur = conn.cursor()
	cur.execute("INSERT INTO public_keys(userid, exponent, modulus) VALUES(?, ?, ?)", (userid, pkey[1], str(pkey[3])))
	conn.commit()
	cur.close()
	conn.close()
else:
	print("An error occured during the configuration: Could not find public key")

connection.disconnect()

print("Your card has been configured")




