#!/usr/bin/env python3

# APDU to select the good applet on the chip
SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08] 

GP_PATH = "../GlobalPlatformPro/gp.jar"
BIN_PATH = "../bin/Paystival221.cap"
PIN = "31323334"
AID_STR = "0102030405"

# AID to select the applet on the card
AID = [0x01, 0x02, 0x03, 0x04, 0x05, 0x01, 0x02, 0x03]
apdu = SELECT + AID

