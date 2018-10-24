package storm.math.interpol;

import storm.com.*;
import storm.math.*;

import java.util.stream.*;

abstract class ExtrapolationFunction implements Interpolation.ResettableFunction {

	enum EndPoint {
		Left(Direction.Left), Right(Direction.Right);

		private final Direction direction;

		EndPoint(Direction d) {
			direction = d;
		}

		double get(double[] x) {
			return x[this == Left ? 0 : x.length - 1];
		}
	}

	private final Localizer localizer = new BisectLocalizer();
	protected final double[] x;
	protected final double[] y;

	ExtrapolationFunction(double[] x, double[] y) {
		Assure.that(x.length > 0, () -> "Empty interpolation grid");
		Assure.sameSize(x, y, () -> "X-vector and Y-vector of interpolation");
		this.x = x;
		this.y = y;
	}

	protected static double[] d(double[] x) {
		/* d1 performs 4 to 5 times faster than stream-version d2 */
		return d1(x);
	}

	class FiniteDifferences {
		private final double[] dx;
		private double[] dy;
		private double[] dydx;

		double[] dx() {return dx;}

		double[] dy() {return dy;}

		double[] dydx() {return dydx;}

		FiniteDifferences(double[] x, double[] y) {
			dx = d(x);
			updateY(y);
		}

		void updateY(double[] y) {
			dy = d(y);
			dydx = Doubles.operate(dx, dy, (dxi, dyi) -> dyi / dxi);
		}

	}

	static double[] d1(double[] x) {
		double dx[] = new double[x.length - 1];
		for (int i = 0; i < x.length - 1; ++i) {
			dx[i] = x[i + 1] - x[i];
		}
		return dx;
	}

	static double[] d2(double[] x) {
		return IntStream.range(0, x.length - 1).mapToDouble(i -> x[i + 1] - x[i]).toArray();
	}

	@Override
	public void updateY(double[] y) {
		System.arraycopy(y, 0, this.y, 0, y.length);
	}

	@Override
	public DoubleValue at(double x) {
		if (x < EndPoint.Left.get(this.x)) {
			return extrapolate(x, EndPoint.Left);
		} else if (x > EndPoint.Right.get(this.x)) {
			return extrapolate(x, EndPoint.Right);
		} else {
			int i = localizer.getIntervalIndex(x, this.x);
			if (i >= 0) {
				return () -> y[i];
			}
			return interpolateInner(x, -i - 2);
		}
	}

	protected abstract DoubleValue extrapolate(double x, EndPoint left);

	protected abstract DoubleValue interpolateInner(double x, int i);

}
