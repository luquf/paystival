#!/usr/bin/env python3

import hashlib

class Transaction:
	
	def __init__(self, byte_array):
		self.byte_array = byte_array
		self.amount = ((byte_array[0]<<8)|(byte_array[1]&0xFF))
		self.type = byte_array[2]
		self.from_ = 0
		self.to = 0
		self.hash = 0
		self.trans_type = ["CREDIT", "DEBIT"]
		for i in range(0, 4):
			self.from_ = (self.from_<<8)|(byte_array[i+3]&0xFF)
		for i in range(0, 4):
			self.to = (self.to<<8)|(byte_array[i+7]&0xFF)
		for i in range(0, 20): # currently sha1
			self.hash = (self.hash<<8)|(byte_array[i+11]&0xFF)
	
	def verify_transaction(self):
		hash_obj = hashlib.sha1(bytearray(self.byte_array[:11]))
		a = hash_obj.hexdigest()
		if int(a, 16) == self.hash:
			return True
		return False

	def __str__(self):
		return f"amount:{self.amount}€, type:{self.trans_type[self.type]}, from:{hex(self.from_)[2:]}, to:{hex(self.to)[2:]}, hash:{hex(self.hash)[2:]}"
		
		

