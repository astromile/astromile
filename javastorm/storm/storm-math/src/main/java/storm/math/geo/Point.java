package storm.math.geo;

import java.util.*;

public class Point implements PointR2 {
	public static final Point ORIGIN = new Point(0, 0);
	private final double x;
	private final double y;

	public Point(double x, double y) {
		this.x = x;
		this.y = y;
	}

	public Point add(Point other) {
		return new Point(x + other.x, y + other.y);
	}

	public Point sub(Point other) {
		return new Point(x - other.x, y - other.y);
	}

	public Point mul(double scale) {
		return new Point(scale * x, scale * y);
	}

	public Point div(double denominator) {
		return new Point(x / denominator, y / denominator);
	}

	public double distanceTo(Point other) {
		double dx = x - other.x, dy = y - other.y;
		return Math.sqrt(dx * dx + dy * dy);
	}

	public static Comparator<Point> getComparatorByX() {
		return Comparator.comparing(p -> p.x);
	}

	@Override
	public double x() {
		return x;
	}

	@Override
	public double y() {
		return y;
	}
}


