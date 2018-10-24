package storm.math.interpol;

public enum Direction {

	Left(-1), Right(1);

	private final int direction;

	Direction(int i) {direction = i;}

	public int asInt() {return direction;}

	public double asDouble() {return direction;}
}
