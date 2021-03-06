package wallet;

import javacard.security.MessageDigest;
import javacard.framework.*;
import wallet.Transaction;

public class TransactionManager {

	private Transaction[] transactions;
	private short length;

	public TransactionManager() {
		this.transactions = new Transaction[500];
		this.length = 0;
	}

	public short getLength() {
		return this.length;
	}	
	
	public boolean storeTransaction(Transaction t) {
		if (length < (short)500) {
			transactions[length] = t;
			length++;
			return true;
		}
		return false;
	}

	public Transaction getTransaction(short i) {
		if (i < 0 || i > 499) {
			return null;
		}
		return this.transactions[i];
	}

}

