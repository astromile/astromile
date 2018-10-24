package storm.fin.com;

public enum Direction {

	Undefined(0), Forward(1), Backward(-1);

	private final int direction;

	Direction(int direction) {
		this.direction = direction;
	}

	public static Direction of(int delta) {
		if (delta > 0) {
			return Forward;
		} else if (delta < 0) {
			return Backward;
		}
		return Undefined;
	}

	/**
	 * @return +1 for {@code Forward} and -1 for {@code Backward}
	 */
	public int getValue() {
		return direction;
	}

	public Direction opposite() {
		return of(-direction);
	}
}
