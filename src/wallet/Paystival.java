package wallet;

import javacard.framework.*;
import javacard.security.*;
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
	
	/* General settings */ 
	private static final byte PIN_MAX_TRIES = (byte)0x05;
	private static final byte PIN_LENGTH = (byte)0x04;
	
	/* Balance can be between 0 and 1000 euros */
	private static final short MAX_BALANCE = (short)0x3e8;
	private static final short MIN_BALANCE = (short)0x0;
	private static final byte MAX_TRANS = (byte)0x32;
	
	/* Exceptions */
	private static final short SW_INSUFFICIENT_FUNDS = (short)0x9900;
	private static final short SW_BALANCE_LIMIT = (short)0x9901;
	private static final short SW_INVALID_PIN = (short)0x9804;
	private static final short SW_UNAUTH_ACCESS = (short)0x9808;
	private static final short SW_INVALID_TRANS_ID = (short)0x9902;
	
	private static final short INFO_LENGTH = (short)0x80;
	
	private OwnerPIN userPIN;
	private short balance;
	private static KeyPair ECKeyPair;
	private byte information[];

	/* Logging of the transactions on the card */
	private TransactionManager manager;
	
	private Paystival(byte bArray[], short bOffset, byte bLength) {
	
		/* Max of 5 try, pin composed of 4 numbers */
		userPIN = new OwnerPIN(PIN_MAX_TRIES, PIN_LENGTH);

		/* Transaction manager storage in memory */
		manager = new TransactionManager();
	
		/* Calculating the offset for the hardcoded parameter */
		byte iLen = bArray[bOffset];
		bOffset = (short)(bOffset+iLen+0x1);
		byte cLen = bArray[bOffset];
		bOffset = (short)(bOffset+cLen+0x1);
		byte aLen = bArray[bOffset];
	
	
		byte pinLen = 0x04;
		userPIN.update(bArray, (short)(bOffset+1), pinLen);
	
		this.information = new byte[INFO_LENGTH];
		Util.arrayCopy(bArray, (short)((bOffset+1)+(short)pinLen), information, (short)0, INFO_LENGTH);
	
		/* Generates EC key pair */
		try {
			ECKeyPair = new KeyPair(KeyPair.ALG_EC_F2M, KeyBuilder.LENGTH_EC_F2M_193);
			ECKeyPair.genKeyPair();
		} catch (CryptoException c) {
			short reason = c.getReason();
			ISOException.throwIt(reason);
		}
	
		balance = (short)0x114; /* 276 € */
	
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
			a = (short)((buffer[5]<<8)|(buffer[6]&0xFF));
			validated = this.debit(a);
			if (!validated) {
				ISOException.throwIt(SW_INSUFFICIENT_FUNDS); /* Insufficient funds */	
			} else {
				/* Log the transcation */
				byte[] from = new byte[4];
				Util.arrayCopy(information, (short)40, from, (short)0, (short)4);
				Transaction td = new Transaction(a, from, new byte[]{(byte)0xff, (byte)0xff, (byte)0xff, (byte)0xff}, Transaction.DEBIT);
				manager.storeTransaction(td);
			}
			break;
	
		case INS_CREDIT_BALANCE:
			if (!userPIN.isValidated()) {
				ISOException.throwIt(SW_UNAUTH_ACCESS); /* Unauthenticated access */	
			}
			a = (short)((buffer[5]<<8)|(buffer[6]&0xFF));
			validated = this.credit(a);
			if (!validated) {
				ISOException.throwIt(SW_BALANCE_LIMIT); /* Balance limit */	
			} else {
				/* Log the transcation */
				byte[] to = new byte[4];
				Util.arrayCopy(information, (short)40, to, (short)0, (short)4);
				Transaction td = new Transaction(a, to, Transaction.CREDIT);
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
			Util.arrayCopyNonAtomic(information, (short)0, buffer, (short)0, INFO_LENGTH);
			apdu.setOutgoingAndSend((short) 0, INFO_LENGTH);
	
			break;

		case INS_REQUEST_TRANS:
			short tid = (short)((buffer[5]<<8)|(buffer[6]&0xFF));
			Transaction t = manager.getTransaction(tid);
			if (t == null)
				ISOException.throwIt(SW_INVALID_TRANS_ID); /* Invalid transaction ID */	
			byte[] infos = t.getTransactionData();
			Util.arrayCopyNonAtomic(infos, (short)0, buffer, (short)0, (short)infos.length);
			apdu.setOutgoingAndSend((short) 0, (short)infos.length);
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
	
}
