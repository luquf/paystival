# INF648: Embedded security/side channel attack project; javacard

This project aims to implement a cashless payment system for festivals based on the javacard environment.

## Requirements
- Linux based system
- Python3
- Openssl
- GlobalPlatformPro command line tools in $PATH 
```console
foo@bar:~$ echo "alias gpj='java -jar $HOME/path/to/GlobalPlatformPro/gp.jar'" >> ~/.bash_aliases
foo@bar:~$ source ~/.bash_aliases
```

## Installation

Download the project
```console
foo@bar:~$ git clone https://github.com/luquf/paystival
foo@bar:~$ cd paystival
```
Create and activate the python virtual environment
```console
foo@bar:~$ virtualenv env --python=python3
foo@bar:~$ source env/bin/activate
```
Install the dependancies
```console
foo@bar:~$ python -m pip install -r requirements.txt
```

## Running the project
Setup the database for a new use
```console
foo@bar:~$ make setup
```
Create a new pair of ECDSA keys for the festival
```console
foo@bar:~$ make keys
```
Run the flow machines graphical interface
```console
foo@bar:~$ make client
```
Run the cashier machine graphical interface
```console
foo@bar:~$ make cashier
```

