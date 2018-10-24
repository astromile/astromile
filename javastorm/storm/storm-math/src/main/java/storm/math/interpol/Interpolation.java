package storm.math.interpol;

import storm.com.*;
import storm.math.geo.*;

import java.util.*;
import java.util.concurrent.atomic.*;

public interface Interpolation {
	interface Function {
		DoubleValue at(double x);
	}

	interface ResettableFunction extends Function {
		void updateY(double[] y);
	}

	/**
	 * Generates interpolation function based on given x,y
	 *
	 * @param x expected to be sorted and of the same size as {@code y}
	 */
	Function interpolate(double[] x, double[] y);

	default ResettableFunction interpolateResettable(double[] x, double[] y) {
		AtomicReference<Function> f = new AtomicReference<>(interpolate(x, y));
		return new ResettableFunction() {
			@Override
			public void updateY(double[] yNew) {
				f.set(interpolate(x, y));
			}

			@Override
			public DoubleValue at(double x) {
				return f.get().at(x);
			}
		};
	}

	/**
	 * Generates interpolation function based on given list of sorted (w.r.t. x) points
	 */
	default Function interpolate(List<Point> p) {
		double[] x = p.stream().mapToDouble(Point::x).toArray();
		double[] y = p.stream().mapToDouble(Point::y).toArray();
		return interpolate(x, y);
	}

	static LinearInterpolation linear(LinearInterpolation.ExtrapolationMethod extrapolation) {
		return new LinearInterpolation(extrapolation);
	}
}
