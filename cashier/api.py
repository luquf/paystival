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

def is_card_connected():
	r = readers()
	return len(r) > 0

def select_applet(connection):
	data, sw1, sw2 = connection.transmit(apdu)
	if sw1 != 0x90 or sw2 != 0x0:
		return False
	return True

def create_connection():
	r = readers()
	if len(r) == 0:
		return None
	try:
		connection = r[0].createConnection()
		connection.connect()
		ok = select_applet(connection)
		if not ok:
			return None
		return connection
	except:
		return None


def close_connection(connection):
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

def request_user_infos(connection):
	Le = 0x0
	data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_INFO,P1,P2,Le])
	if sw1 == 0x90 and sw2 == 0x00:
		infos = parse_user_info(data)	
		return infos
	else:
		None

def debit_balance(connection, amount):
	# first request the user infos
	infos = request_user_infos(connection)
	if infos is None:
		return False
	# then request a challenge from the card
	enc = None
	Le = 0x0
	data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_CHALLENGE,P1,P2,Le])
	if sw1 == 0x90 and sw2 == 0x00:
		conn = connect("../res/pk_infra.sqlite")	
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

		# now debit the card
		Le = 0x42
		data, sw1, sw2 = connection.transmit([CLA,INS_DEBIT_BALANCE,P1,P2,Le]+[(amount>>8)&0xFF, amount&0xFF]+enc)
		if sw1 == 0x90 and sw2 == 0x00:
			return True
		else:
			return False
	else:
		return False

def credit_balance(connection, amount):
	# first request the user infos
	infos = request_user_infos(connection)
	if infos is None:
		return False
	# then request a challenge from the card
	enc = None
	Le = 0x0
	data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_CHALLENGE,P1,P2,Le])
	if sw1 == 0x90 and sw2 == 0x00:
		conn = connect("../res/pk_infra.sqlite")	
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

		# now credit the card
		Le = 0x42
		data, sw1, sw2 = connection.transmit([CLA,INS_CREDIT_BALANCE,P1,P2,Le]+[(amount>>8)&0xFF, amount&0xFF]+enc)
		if sw1 == 0x90 and sw2 == 0x00:
			return True
		else:
			return False
	else:
		return False

def ask_and_store_public_key(connection, userid):
	Le = 0x0
	data, sw1, sw2 = connection.transmit([CLA,INS_REQUEST_PUB_KEY,P1,P2,Le])
	if sw1 == 0x90 and sw2 == 0x00:
		pkey = get_card_public_key(data)
		conn = connect("../res/pk_infra.sqlite")
		cur = conn.cursor()
		cur.execute("INSERT INTO public_keys(userid, exponent, modulus) VALUES(?, ?, ?)", (userid, pkey[1], str(pkey[3])))
		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		return False


