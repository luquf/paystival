#!/usr/bin/env python3

# APDU to select the good applet on the chip
SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08] 

HOME_PATH = "../"
GP_PATH = HOME_PATH + "GlobalPlatformPro/gp.jar"
BIN_PATH = HOME_PATH + "bin/Paystival221.cap"

# Applet selector
AID_STR = "0102030405"

# AID to select the applet on the card
AID = [0x01, 0x02, 0x03, 0x04, 0x05, 0x01, 0x02, 0x03]

# APDU to select the card
apdu = SELECT + AID

# Instructions available on the card
INS_VERIFY_PIN = 0x01
INS_DEBIT_BALANCE = 0x02
INS_CREDIT_BALANCE = 0x03
INS_REQUEST_BALANCE = 0x04
INS_REQUEST_INFO = 0x05
INS_REQUEST_TRANS = 0x06
INS_REQUEST_PUB_KEY = 0x07
INS_REQUEST_CHALLENGE = 0x08
INS_REQUEST_TRANSACTION = 0x09

CLA = 0xA0
P1 = 0x00	
P2 = 0x00
Le = 0x00 	

