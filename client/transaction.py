#!/usr/bin/env python3

from Crypto.Hash import SHA256
from sqlite3 import *
from utils import *
from Crypto.PublicKey.RSA import *
import rsa

class Transaction:
	
	def __init__(self, byte_array):
		self.byte_array = byte_array
		self.amount = ((byte_array[0]<<8)|(byte_array[1]&0xFF))
		self.type = byte_array[2]
		self.tid = 0
		self.from_ = 0
		self.to = 0
		self.sig = 0
		self.trans_type = ["CREDIT", "DEBIT"]
		for i in range(0, 8):
			self.tid = (self.tid<<8)|(byte_array[i+3]&0xFF)
		for i in range(0, 4):
			self.from_ = (self.from_<<8)|(byte_array[i+11]&0xFF)
		for i in range(0, 4):
			self.to = (self.to<<8)|(byte_array[i+15]&0xFF)
		for i in range(0, 64): # currently sha1
			self.sig = (self.sig<<8)|(byte_array[i+19]&0xFF)
	
	def verify_transaction(self):
		data = bytearray(self.byte_array[:19])
		userid = ""
		conn = connect("../res/paystival.sqlite")	
		cur = conn.cursor()
		if self.type == 0:
			userid = to2hex(self.to)
		else:
			userid = to2hex(self.from_)
		cur.execute("SELECT exponent, modulus FROM public_keys WHERE userid=?", (userid,))
		r = cur.fetchall()
		cur.close()
		conn.close()
		pubkey = construct((int(r[0][1], 10), r[0][0]))
		try:
			rsa.verify(bytes(data), self.sig.to_bytes(64, "big"), pubkey)
			return True
		except:
			return False

	def __str__(self):
		return f"amount:{self.amount}€, type:{self.trans_type[self.type]}, id:{hex(self.tid)[2:]} from:{hex(self.from_)[2:]}, to:{hex(self.to)[2:]}, sig:{hex(self.sig)[2:]}"
		
		

