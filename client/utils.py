#!/usr/bin/env python3

def get_card_public_key(data, endian="big"):
	exp_len = (data[0]<<8)|(data[1]&0xFF)
	exp = int.from_bytes(data[2:exp_len+2], endian)
	mod_len = (data[exp_len+2]<<8)|(data[exp_len+3]&0xFF)
	mod = int.from_bytes(data[exp_len+4:exp_len+mod_len+4], endian)
	return exp_len, exp, mod_len, mod

def to2hex(val):
	fmt = "%0.2x" % val
	return fmt.format(val)

def get_pin_from_str(pin):
	return [ord(c) for c in pin]

def print_ret_codes(sw1, sw2):
	print(hex(sw1), hex(sw2))


def get_unpad(value):
	ret = ""
	for i in range(0, len(value)):
		v = value[i]
		if v != 0:
			ret += chr(v)
		else:
			return ret

def pad_array(arr, length, val=0x0):
	if len(arr) > length:
		return arr
	while len(arr) < length:
		arr.append(val)
	return arr

def array_to_hexdigest(array):
	ret = ""
	for v in array:
		ret += to2hex(v)
	return ret

def str2hex(s):
	arr = [ord(c) for c in s]
	return array_to_hexdigest(arr)

def hex2str(h):
	ret = ""
	for i in range(0, len(h), 2):
		ret += chr(int(h[i:i+2], 16))
	return ret

def hex_to_array(val):
	ret = []
	for i in range(0, len(val), 2):
		ret.append(int(val[i:i+2], 16))
	return ret

def parse_user_info(info):
	first_name = info[:20]
	last_name = info[20:40]
	userid = info[40:44]
	sig = info[44:108]
	return first_name, last_name, userid, sig
