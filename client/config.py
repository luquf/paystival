#!/usr/bin/env python3

# APDU to select the good applet on the chip
SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08] 

HOME_PATH = "../"
GP_PATH = HOME_PATH + "GlobalPlatformPro/gp.jar"
BIN_PATH = HOME_PATH + "bin/Paystival221.cap"

# Card paremeters stored to be written in EEPROM
PIN = "31323334" # [0x31, 0x32, 0x33, 0x34] => "1234"

# Applet selector
AID_STR = "0102030405"

# AID to select the applet on the card
AID = [0x01, 0x02, 0x03, 0x04, 0x05, 0x01, 0x02, 0x03]

# APDU to select the card
apdu = SELECT + AID

