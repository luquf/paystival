#!/bin/bash

f="res/paystival.sqlite"
echo "" > $f
sqlite3 $f "CREATE TABLE public_keys (userid VARCHAR(8), exponent INT, modulus TEXT)" ".exit"
echo "Database is ready..."
