package storm.fin.com;

public enum Side {
	Buy(1), Mid(0), Sell(-1);

	private final int value;

	Side(int value) {this.value = value;}

	public int getValue() {return value;}
}
