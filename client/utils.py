#!/usr/bin/env python3

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

def parse_user_info(info):
	first_name = info[:20]
	last_name = info[20:40]
	userid = info[40:44]
	sig = info[44:116]
	return first_name, last_name, userid, sig
