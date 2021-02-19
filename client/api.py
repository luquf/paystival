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

def ask_balance_with_pin(pin, action="balance"):
	r = readers()
	connection = r[0].createConnection()
	connection.connect()
	data, sw1, sw2 = connection.transmit(apdu)
	if sw1 != 0x90 or sw2 != 0x0:
		return -1
	Le = 0x04
	data, sw1, sw2 = connection.transmit([CLA,INS_VERIFY_PIN,P1,P2,Le]+pin)
	if sw1 == 0x90 and sw2 == 0x00:
		Le = 0x0
		data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
		connection.disconnect()
		if sw1 == 0x90 and sw2 == 0x00:
			amount = data[0]
			amount = (amount << 8) | data[1]
			return amount
		return -1
	return -1

