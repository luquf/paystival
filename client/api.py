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

def create_connection():
	r = readers()
	if len(r) == 0:
		return None
	try:
		connection = r[0].createConnection()
		connection.connect()
		return connection
	except:
		return None

def select_applet(connection):
	data, sw1, sw2 = connection.transmit(apdu)
	if sw1 != 0x90 or sw2 != 0x0:
		return False
	return True

def close_connecton(connection):
	return connection.disconnect()

def ask_pin_validation(connection, pin):
	Le = 0x04
	data, sw1, sw2 = connection.transmit([CLA,INS_VERIFY_PIN,P1,P2,Le]+pin)
	if sw1 == 0x90 and sw2 == 0x00:
		return True
	return False

def ask_balance(connection):
	Le = 0x0
	data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_BALANCE,P1,P2,Le])
	if sw1 == 0x90 and sw2 == 0x00:
		amount = data[0]
		amount = (amount << 8) | data[1]
		return amount
	return -1

def ask_and_store_public_key(connection):
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
		return True
	else:
		return False


