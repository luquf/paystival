package wallet;

import javacard.framework.*;
import javacard.security.*;
import javacardx.crypto.*;
import wallet.Transaction;
import wallet.TransactionManager;

public class Paystival extends Applet {

	private static final byte CLA_MONAPPLET = (byte) 0xA0;
	
	/* Possible instructions */
	private static final byte INS_VERIFY_PIN = (byte)0x01;
	private static final byte INS_DEBIT_BALANCE = (byte)0x02;
	private static final byte INS_CREDIT_BALANCE = (byte)0x03;
	private static final byte INS_REQUEST_BALANCE = (byte)0x04;
	private static final byte INS_REQUEST_INFO = (byte)0x05;
	private static final byte INS_REQUEST_TRANS = (byte)0x06;
	private static final byte INS_REQUEST_PUB_KEY = (byte)0x07;
	private static final byte INS_REQUEST_CHALLENGE = (byte)0x08;
	
	/* General settings */ 
	private static final byte PIN_MAX_TRIES = (byte)0x05;
	private static final byte PIN_LENGTH = (byte)0x04;
	
	/* Balance can be between 0 and 1000 euros */
	private static final short MAX_BALANCE = (short)0x3e8;
	private static final short MIN_BALANCE = (short)0x0;
	private static final byte MAX_TRANS = (byte)0x3e8;
	
	/* Exceptions */
	private static final short SW_INSUFFICIENT_FUNDS = (short)0x9900;
	private static final short SW_BALANCE_LIMIT = (short)0x9901;
	private static final short SW_INVALID_PIN = (short)0x9804;
	private static final short SW_UNAUTH_ACCESS = (short)0x9808;
	private static final short SW_INVALID_TRANS_ID = (short)0x9902;
	private static final short SW_KEY_ALREADY_REQUESTED = (short)0x9903;
	private static final short SW_INVALID_CHALLENGE_CIPHER = (short)0x9904;
	
	private static final short INFO_LENGTH = (short)0x80;
	private static final short CHALL_LENGTH = (short)0x40;

	private byte key_requested = 0;
	private byte[] challenge;
	
	private OwnerPIN userPIN;
	private short balance;
	private byte information[];
	private RSAPrivateCrtKey rsaPrivateKey;
	private RSAPublicKey rsaPublicKey;
	private KeyPair kp;


	/* Logging of the transactions on the card */
	private TransactionManager manager;
	
	private Paystival(byte bArray[], short bOffset, byte bLength) {
	
		/* Max of 5 try, pin composed of 4 numbers */
		userPIN = new OwnerPIN(PIN_MAX_TRIES, PIN_LENGTH);

		/* Transaction manager storage in memory */
		manager = new TransactionManager();
	
		/* Calculating the offset for the hardcoded parameters */
		byte iLen = bArray[bOffset];
		bOffset = (short)(bOffset+iLen+0x1);
		byte cLen = bArray[bOffset];
		bOffset = (short)(bOffset+cLen+0x1);
		byte aLen = bArray[bOffset];
	
	
		byte pinLen = 0x04;
		userPIN.update(bArray, (short)(bOffset+1), pinLen);

		this.challenge = new byte[CHALL_LENGTH];
	
		this.information = new byte[INFO_LENGTH];
		Util.arrayCopy(bArray, (short)((bOffset+1)+(short)pinLen), information, (short)0, INFO_LENGTH);
	
		/* Generates asymmetrical key pair (RSA 512 bits) */
		try {
			this.kp = new KeyPair(KeyPair.ALG_RSA_CRT, (short)512);
			kp.genKeyPair();
			rsaPrivateKey = (RSAPrivateCrtKey)kp.getPrivate();
			rsaPublicKey = (RSAPublicKey)kp.getPublic();	
		} catch (CryptoException c) {
			short reason = c.getReason();
			ISOException.throwIt(reason);
		}
	
		balance = (short)0x0; /* 0 € */
	
		register();
	}
	
	
	public static void install(byte bArray[], short bOffset, byte bLength) throws ISOException {
		new Paystival(bArray, bOffset, bLength);
	}
	
	
	public void process(APDU apdu) throws ISOException {
	
		byte[] buffer = apdu.getBuffer();
		
		if (this.selectingApplet()) return;
		
		if (buffer[ISO7816.OFFSET_CLA] != CLA_MONAPPLET) {
		        ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
		}
	
		boolean validated;
		short a;
	
		switch (buffer[ISO7816.OFFSET_INS]) {
	
		case INS_VERIFY_PIN:
			byte byteStream = (byte)(apdu.setIncomingAndReceive());
	    	if (userPIN.check(buffer, ISO7816.OFFSET_CDATA, byteStream) == false) {
				ISOException.throwIt(SW_INVALID_PIN); /* Wrong PIN */	
			}
		    break;

		case INS_DEBIT_BALANCE:
			if (!userPIN.isValidated()) {
				ISOException.throwIt(SW_UNAUTH_ACCESS); /* Unauthenticated access */	
			}

			/* Verify the challenge, TODO: check challenge has been asked */
			boolean ok = this.verifyChallenge(buffer, (short)(ISO7816.OFFSET_CDATA+(short)2));
			if (!ok) {
				ISOException.throwIt(SW_INVALID_CHALLENGE_CIPHER); /* Invalid challenge cipher */	
			}

			a = (short)((buffer[ISO7816.OFFSET_CDATA]<<8)|(buffer[ISO7816.OFFSET_CDATA+1]&0xFF));
			validated = this.debit(a);
			if (!validated) {
				ISOException.throwIt(SW_INSUFFICIENT_FUNDS); /* Insufficient funds */	
			} else {
				/* Log the transcation */
				byte[] from = new byte[4];
				Util.arrayCopy(information, (short)40, from, (short)0, (short)4);
				Transaction td = new Transaction(a, from, new byte[]{(byte)0xff, (byte)0xff, (byte)0xff, (byte)0xff}, Transaction.DEBIT, this.rsaPrivateKey);
				manager.storeTransaction(td);
			}
			break;
	
		case INS_CREDIT_BALANCE:
			if (!userPIN.isValidated()) {
				ISOException.throwIt(SW_UNAUTH_ACCESS); /* Unauthenticated access */	
			}

			/* Verify the challenge, TODO: check challenge has been asked */
			ok = this.verifyChallenge(buffer, (short)(ISO7816.OFFSET_CDATA+(short)2));
			if (!ok) {
				ISOException.throwIt(SW_INVALID_CHALLENGE_CIPHER); /* Invalid challenge cipher */	
			}

			a = (short)((buffer[ISO7816.OFFSET_CDATA]<<8)|(buffer[ISO7816.OFFSET_CDATA+1]&0xFF));
			validated = this.credit(a);
			if (!validated) {
				ISOException.throwIt(SW_BALANCE_LIMIT); /* Balance limit */	
			} else {
				/* Log the transcation */
				byte[] to = new byte[4];
				Util.arrayCopy(information, (short)40, to, (short)0, (short)4);
				Transaction td = new Transaction(a, to, Transaction.CREDIT, this.rsaPrivateKey);
				manager.storeTransaction(td);
			}
			break;
	
		case INS_REQUEST_BALANCE:
			if (!userPIN.isValidated()) {
				ISOException.throwIt(SW_UNAUTH_ACCESS); /* Unauthenticated access */	
			}
			short out = apdu.setOutgoing();
			apdu.setOutgoingLength((short)2);
			
			buffer[0] = (byte)(this.balance>>8);
			buffer[1] = (byte)(this.balance&0xFF);
	
			apdu.sendBytes((short)0, (short)2);
			break;
	
		case INS_REQUEST_INFO:
			Util.arrayCopy(information, (short)0, buffer, (short)0, INFO_LENGTH);
			apdu.setOutgoingAndSend((short) 0, INFO_LENGTH);
			break;

		case INS_REQUEST_TRANS:
			short tid = (short)((buffer[ISO7816.OFFSET_CDATA]<<8)|(buffer[ISO7816.OFFSET_CDATA+1]&0xFF));
			Transaction t = manager.getTransaction(tid);
			if (t == null)
				ISOException.throwIt(SW_INVALID_TRANS_ID); /* Invalid transaction ID */	
			byte[] infos = t.getTransactionData();
			Util.arrayCopy(infos, (short)0, buffer, (short)0, (short)infos.length);
			apdu.setOutgoingAndSend((short) 0, (short)infos.length);
			break;

		case INS_REQUEST_PUB_KEY:
			if (key_requested == 0) {
				short offset = this.serializeKey(buffer, (short)0);
				apdu.setOutgoingAndSend((short) 0, offset);
				key_requested = 1;
			} else {
				ISOException.throwIt(SW_KEY_ALREADY_REQUESTED); /* Key already requested */	
			}
			break;

		case INS_REQUEST_CHALLENGE:
			RandomData random = RandomData.getInstance(RandomData.ALG_SECURE_RANDOM);
			random.setSeed(this.challenge, (short)0, CHALL_LENGTH);
			random.generateData(this.challenge, (short)0, CHALL_LENGTH);
			Util.arrayCopyNonAtomic(this.challenge,(short)0, buffer, (short)0, CHALL_LENGTH);
			apdu.setOutgoingAndSend((short)0, CHALL_LENGTH);
			break;
		
		default:
	    	ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
		}
	}
	
	public boolean debit(short amount) {
		if ((short)(this.balance - amount) < MIN_BALANCE) {
			return false;
		}
		this.balance -= amount;
		return true;
	}
	
	public boolean credit(short amount) {
		if ((short)(MAX_BALANCE - this.balance) < amount){
			return false;
		}
		else if (amount > MAX_TRANS) {
			return false;
		}
		this.balance += amount;
		return true;
	}
	
	
	public short requestBalance() {
		return this.balance;
	}

	private final short serializeKey(byte[] buffer, short offset) {
		short expLen = this.rsaPublicKey.getExponent(buffer, (short) (offset + 2));
		Util.setShort(buffer, offset, expLen);
		short modLen = this.rsaPublicKey.getModulus(buffer, (short) (offset + 4 + expLen));
		Util.setShort(buffer, (short) (offset + 2 + expLen), modLen);
		return (short) (4 + expLen + modLen);
	}

	public boolean verifyChallenge(byte[] inBuffer, short offset) {
		byte[] uncipheredChallenge = new byte[64];
		Cipher rsaCipher = Cipher.getInstance(Cipher.ALG_RSA_NOPAD, false);
		rsaCipher.init(rsaPrivateKey, Cipher.MODE_DECRYPT);

		/* Perform decryption */
		short outLen = rsaCipher.doFinal(inBuffer, offset, (short)64, uncipheredChallenge, (short)0);
		byte ok = Util.arrayCompare(uncipheredChallenge, (short)0, this.challenge, (short)0, CHALL_LENGTH);

		/* Reset the challenge after verification */
		this.challenge = new byte[CHALL_LENGTH];
		if (ok == 0) {
			return true;
		}
		return false;
	}
}
