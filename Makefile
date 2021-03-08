CC=gpj
INSTALL=bin/Paystival221.cap
DELETE=0102030405
GPJ=java -jar GlobalPlatformPro/gp.jar

.PHONY: list build client cashier setup keys

delete:
	@$(GPJ) -delete $(DELETE)
	@echo "Card's applet deleted..."

build:
	@ant 

list:
	@$(GPJ) -l

clean:
	@rm -rf $(INSTALL)
	@echo "Binary applet removed..."

keys:
	@rm -rf keys/*.pem
	@openssl ecparam -name prime256v1 -genkey -out keys/sk.pem
	@openssl ec -in keys/sk.pem -pubout -out keys/vk.pem
	@chmod 600 keys/sk.pem
	@echo "Fresh pair of ECDSA keys created..."

setup:
	@./setup.sh

client:
	@(cd client && python main.py&)

cashier:
	@(cd cashier && python main.py&)
