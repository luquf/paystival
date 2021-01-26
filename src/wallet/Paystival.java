package wallet;

import javacard.framework.*;
import javacard.security.*;

public class Paystival extends Applet {

    private static final byte CLA_MONAPPLET = (byte) 0xA0;

	/* Possible instructions */
    private static final byte INS_VERIFY_PIN = (byte)0x01;
    private static final byte INS_DEBIT_BALANCE = (byte)0x02;
    private static final byte INS_CREDIT_BALANCE = (byte)0x03;
    private static final byte INS_REQUEST_BALANCE = (byte)0x04;
    private static final byte INS_REQUEST_CARD_INFO = (byte)0x05;
    private static final byte INS_REQUEST_CARD_INFO_SIG = (byte)0x06;

	/* General settings */ 
	private static final byte PIN_MAX_TRIES = (byte)0x05;
	private static final byte PIN_LENGTH = (byte)0x04;

	/* Balance can be between 0 and 500 euros */
	private static final short MAX_BALANCE = (short)0x1f4;
	private static final short MIN_BALANCE = (short)0x0;
	private static final byte MAX_TRANS = (byte)0x32;

	/* Exceptions */
	private static final short SW_INSUFFICIENT_FUNDS = (short)0x9900;
	private static final short SW_BALANCE_LIMIT = (short)0x9901;
	private static final short SW_INVALID_PIN = (short)0x9804;
	private static final short SW_UNAUTH_ACCESS = (short)0x9808;

	private OwnerPIN userPIN;
	private short balance;
	private static KeyPair ECKeyPair;
	
	private Paystival(byte bArray[], short bOffset, byte bLength) {

		/* Max of 5 try, pin composed of 4 numbers */
		userPIN = new OwnerPIN(PIN_MAX_TRIES, PIN_LENGTH);

		/* Calculating the offset for the hardcoded parameter */
		byte iLen = bArray[bOffset];
		bOffset = (short)(bOffset+iLen+1);
		byte cLen = bArray[bOffset];
		bOffset = (short)(bOffset+cLen+1);
		byte aLen = bArray[bOffset];

		userPIN.update(bArray, (short)(bOffset+1), aLen);

		/* Generates EC key pair */
		try {
			ECKeyPair = new KeyPair(KeyPair.ALG_EC_F2M, KeyBuilder.LENGTH_EC_F2M_193);
			ECKeyPair.genKeyPair();
		} catch (CryptoException c) {
			short reason = c.getReason();
			ISOException.throwIt(reason);
		}

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
			break;

		case INS_CREDIT_BALANCE:
			if (!userPIN.isValidated()) {
				ISOException.throwIt(SW_UNAUTH_ACCESS); /* Unauthenticated access */	
			}
			break;

		case INS_REQUEST_BALANCE:
			if (!userPIN.isValidated()) {
				ISOException.throwIt(SW_UNAUTH_ACCESS); /* Unauthenticated access */	
			}
			break;
		
		default:
	    	ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
		}

	}

	public boolean debit(short amount) {
		return true;

	}

	public boolean credit(short amount) {
		return true;
	}


	public short requestBalance() {
		return this.balance;
	}

}
