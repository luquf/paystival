#!/usr/bin/env python3

from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from utils import *
import sys, os, subprocess


first_name = input("First name: ")
last_name = input("Last name: ")
pin = input("PIN (4 chiffres): ")
amount = input("Amount of money (1-500€): ")
hex_pin = str2hex(pin)

# CARD CREATION PROCESS
with open("../keys/sk.pem") as f:
   sk = SigningKey.from_pem(f.read(), hashlib.sha256)

prenom = "4C656F0000000000000000000000000000000000"
nom = "426572746F6E0000000000000000000000000000"
userid = "DEADBEEF"

data = []
for i in range(0, len(prenom), 2):
	data.append(int(prenom[i:i+2], 16))

for i in range(0, len(nom), 2):
	data.append(int(nom[i:i+2], 16))

for i in range(0, len(userid), 2):
	data.append(int(userid[i:i+2], 16))

new_signature = sk.sign_deterministic(bytearray(data), sigencode=sigencode_der)


#out = subprocess.Popen(['java', '-jar', GP_PATH, '-install', BIN_PATH, '-default', '-params', hex_pin], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print("Your card has been configured")



