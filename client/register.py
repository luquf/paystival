#!/usr/bin/env python3

from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from utils import *
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

data = get_pin_from_str(pin) + first_name + last_name + hex_to_array(userid)

new_signature = sk.sign_deterministic(bytearray(data), sigencode=sigencode_der)
hsig = new_signature.hex()

first_name = array_to_hexdigest(first_name)
last_name = array_to_hexdigest(last_name)
pin = str2hex(pin)

param = pin + first_name + last_name + userid + hsig
param = param.upper()

#out = subprocess.Popen(['java', '-jar', GP_PATH, '-install', BIN_PATH, '-default', '-params', hex_pin], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print("Your card has been configured")



