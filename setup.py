#!/usr/bin/env python3

from sqlite3 import *

conn = connect("storage/pk_infra.sqlite")
cur = conn.cursor()

cur.execute("CREATE TABLE public_keys (userid VARCHAR(8), exponent INT, modulus TEXT)") 

cur.close()
conn.close()
