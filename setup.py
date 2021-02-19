#!/usr/bin/env python3

from sqlite3 import *

with open("storage/pk_infra.sqlite", "w") as f:
	pass

conn = connect("storage/pk_infra.sqlite")
cur = conn.cursor()

cur.execute("CREATE TABLE public_keys (userid VARCHAR(8), exponent INT, modulus TEXT)") 

cur.close()
conn.close()
