#!/usr/bin/env python3

def to_2hex(val):
	fmt = "%0.2x" % val
	return fmt.format(val)

def get_pin_from_str(pin):
	return [ord(c) for c in pin]

def print_ret_codes(sw1, sw2):
	print(hex(sw1), hex(sw2))
