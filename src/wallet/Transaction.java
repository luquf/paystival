package wallet;

import javacard.security.MessageDigest;
import javacard.framework.*;
import javacard.security.*;
import javacardx.crypto.*;

public class Transaction {
	
	public static byte CREDIT = 0x0;
	public static byte DEBIT = 0x1;

	private static final byte TID_LENGTH = 0x8;

	private byte[] tid;             /* 8 bytes */ 
	private short amount; 			/* 2 bytes */
	private byte type;				/* 1 byte, 0 = credit, 1 = debit */
	private byte[] from;			/* 4 bytes */
	private byte[] to;				/* 4 bytes */
	private byte[] sigBuf;	/* 20 bytes */

	private Signature sig;

	public Transaction(short amount, byte[] to, byte type, RSAPrivateCrtKey sk) {
		this.amount = amount;
		this.type = type;
		this.tid = new byte[8];
		this.from = new byte[4]; 	/* 0xFFFFFFFF means this is a credit from the festival*/
		this.to = to; 				/* 0xFFFFFFFF means this is a credit from the festival*/
		this.sigBuf = new byte[64];

		RandomData random = RandomData.getInstance(RandomData.ALG_SECURE_RANDOM);
		random.setSeed(this.tid, (short)0, TID_LENGTH);
		random.generateData(this.tid, (short)0, TID_LENGTH);

		/* Hash the transaction information */
		sig = Signature.getInstance(Signature.ALG_RSA_SHA_PKCS1, false);
		sig.init(sk, Signature.MODE_SIGN);
		byte[] buf = new byte[19];
		buf[0] = (byte)((amount >> 8) & 0xFF);
		buf[1] = (byte)(amount & 0xFF);
		buf[2] = type;
		Util.arrayCopyNonAtomic(tid, (short)0, buf, (short)3, (short)8);
		Util.arrayCopyNonAtomic(from, (short)0, buf, (short)11, (short)4);
		Util.arrayCopyNonAtomic(to, (short)0, buf, (short)15, (short)4);
		short ret = sig.sign(buf, (short)0, (short)19, sigBuf, (short)0);
	}

	public Transaction(short amount, byte[] from, byte[] to, byte type, RSAPrivateCrtKey sk) {
		this.amount = amount;
		this.type = type;
		this.tid = new byte[8];
		this.from = from;
		this.to = to;
		this.sigBuf = new byte[64];

		RandomData random = RandomData.getInstance(RandomData.ALG_SECURE_RANDOM);
		random.setSeed(this.tid, (short)0, TID_LENGTH);
		random.generateData(this.tid, (short)0, TID_LENGTH);

		/* Hash the transaction information */
		sig = Signature.getInstance(Signature.ALG_RSA_SHA_PKCS1, false);
		sig.init(sk, Signature.MODE_SIGN);
		byte[] buf = new byte[19];
		buf[0] = (byte)((amount >> 8) & 0xFF);
		buf[1] = (byte)(amount & 0xFF);
		buf[2] = type;
		Util.arrayCopyNonAtomic(tid, (short)0, buf, (short)3, (short)8);
		Util.arrayCopyNonAtomic(from, (short)0, buf, (short)11, (short)4);
		Util.arrayCopyNonAtomic(to, (short)0, buf, (short)15, (short)4);
		short ret = sig.sign(buf, (short)0, (short)19, sigBuf, (short)0);
	}

	public byte[] getTransactionData() {
		byte buf[] = new byte[83];
		buf[0] = (byte)((amount >> 8) & 0xFF);
		buf[1] = (byte)(amount & 0xFF);
		buf[2] = type;
		Util.arrayCopyNonAtomic(tid, (short)0, buf, (short)3, (short)8);
		Util.arrayCopyNonAtomic(from, (short)0, buf, (short)11, (short)4);
		Util.arrayCopyNonAtomic(to, (short)0, buf, (short)15, (short)4);
		Util.arrayCopyNonAtomic(sigBuf, (short)0, buf, (short)19, (short)64);
		return buf;	
	}
}
