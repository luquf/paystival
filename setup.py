#!/usr/bin/env python3

from sqlite3 import *

with open("res/pk_infra.sqlite", "w") as f:
	pass

conn = connect("res/pk_infra.sqlite")
cur = conn.cursor()

cur.execute("CREATE TABLE public_keys (userid VARCHAR(8), exponent INT, modulus TEXT)") 

cur.close()
conn.close()
