CC=gpj
INSTALL=bin/Paystival221.cap
DELETE=0102030405
GPJ=java -jar /home/luquf/Documents/polytechnique/javacard/DevJavaCard/tools/GlobalPlatformPro/gp.jar
PIN=31323334
FIRST_NAME=Leo
LAST_NAME=BERTON
USERID=1234567812345678
SIGNATURE=deadbeef

install:
	$(GPJ) -install $(INSTALL) -default -params $(PIN)

delete:
	$(GPJ) -delete $(DELETE)

build:
	ant

list:
	$(GPJ) -l

clean:
	rm -rf $(INSTALL)

all:
	ant
	$(GPJ) -delete $(DELETE)
	$(GPJ) -install $(INSTALL) -default -params $(PIN) 

