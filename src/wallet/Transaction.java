package wallet;

import javacard.security.MessageDigest;
import javacard.framework.*;
import javacard.security.*;

public class Transaction {
	
	public static byte CREDIT = 0x0;
	public static byte DEBIT = 0x1;

	private short amount; 			/* 2 bytes */
	private byte type;				/* 1 byte, 0 = credit, 1 = debit*/
	private byte[] from;			/* 4 bytes */
	private byte[] to;				/* 4 bytes */
	private byte[] checkSumHash;	/* 20 bytes */

	private MessageDigest ctx;

	public Transaction(short amount, byte[] to, byte type, RSAPrivateCrtKey sk) {
		this.amount = amount;
		this.type = type;
		this.from = new byte[4];
		this.to = to;
		this.checkSumHash = new byte[20];

		/* Hash the transaction information */
		try {
			ctx = MessageDigest.getInstance(MessageDigest.ALG_SHA, false);
			byte[] buf = new byte[11];
			buf[0] = (byte)((amount >> 8) & 0xFF);
			buf[1] = (byte)(amount & 0xFF);
			buf[2] = type;
			Util.arrayCopyNonAtomic(from, (short)0, buf, (short)3, (short)4);
			Util.arrayCopyNonAtomic(to, (short)0, buf, (short)7, (short)4);
			ctx.doFinal(buf, (short)0, (short)11, checkSumHash, (short)0);
		} catch (Exception e) {}
	}

	public Transaction(short amount, byte[] from, byte[] to, byte type, RSAPrivateCrtKey sk) {
		this.amount = amount;
		this.type = type;
		this.from = from;
		this.to = to;
		this.checkSumHash = new byte[20];

		/* Hash the transaction information */
		try {
			ctx = MessageDigest.getInstance(MessageDigest.ALG_SHA, false);
			byte[] buf = new byte[11];
			buf[0] = (byte)((amount >> 8) & 0xFF);
			buf[1] = (byte)(amount & 0xFF);
			buf[2] = type;
			Util.arrayCopyNonAtomic(from, (short)0, buf, (short)3, (short)4);
			Util.arrayCopyNonAtomic(to, (short)0, buf, (short)7, (short)4);
			ctx.doFinal(buf, (short)0, (short)11, checkSumHash, (short)0);
		} catch (Exception e) {}
	}

	public byte[] getTransactionData() {
		byte buf[] = new byte[43];
		buf[0] = (byte)((amount >> 8) & 0xFF);
		buf[1] = (byte)(amount & 0xFF);
		buf[2] = type;
		Util.arrayCopyNonAtomic(from, (short)0, buf, (short)3, (short)4);
		Util.arrayCopyNonAtomic(to, (short)0, buf, (short)7, (short)4);
		Util.arrayCopyNonAtomic(checkSumHash, (short)0, buf, (short)11, (short)20);
		return buf;	
	}
}
