package storm.math.interpol;

import storm.com.*;
import storm.math.interpol.LinearInterpolation.PiecewiseLinearFunction.*;

class LinearInterpolation implements Interpolation {

	private final ExtrapolationMethod extrapolation;

	LinearInterpolation(ExtrapolationMethod extrapolation) {this.extrapolation = extrapolation;}

	@Override
	public Function interpolate(double[] x, double[] y) {
		return interpolateResettable(x, y);
	}

	@Override
	public ResettableFunction interpolateResettable(double[] x, double[] y) {
		if (extrapolation.left() == Extrapolation.Linear || extrapolation.right() == Extrapolation.Linear) {
			Assure.that(x.length > 1,
					() -> "For linear extrapolation, there should be at least two points");
		}
		return new PiecewiseLinearFunction(x, y, extrapolation);
	}

	interface ExtrapolationMethod {

		Extrapolation left();

		Extrapolation right();

		default Extrapolation get(ExtrapolationFunction.EndPoint e) {
			return e == ExtrapolationFunction.EndPoint.Left ? left() : right();
		}

		static ExtrapolationMethod of(Extrapolation left, Extrapolation right) {
			return new ExtrapolationMethod() {
				@Override
				public Extrapolation left() {
					return left;
				}

				@Override
				public Extrapolation right() {
					return right;
				}
			};
		}
	}

	static class PiecewiseLinearFunction extends ExtrapolationFunction {

		private final FiniteDifferences findif;

		private final ExtrapolationMethod extrapolation;

		PiecewiseLinearFunction(double[] x, double[] y, ExtrapolationMethod extrapolation) {
			super(x, y);
			findif = new FiniteDifferences(x, y);
			this.extrapolation = extrapolation;
		}

		@Override
		protected DoubleValue extrapolate(double x, EndPoint e) {
			return extrapolation.get(e).extrapolate(x, e, this);
		}

		@Override
		protected DoubleValue interpolateInner(double x, int i) {
			double dx = x - this.x[i];
			return () -> y[i] + dx * findif.dydx()[i];
		}

		@Override
		public void updateY(double[] y) {
			super.updateY(y);
			findif.updateY(y);
		}

		enum Extrapolation {
			Constant, Linear;

			DoubleValue extrapolate(double x, ExtrapolationFunction.EndPoint e, PiecewiseLinearFunction f) {
				if (this == Constant) {
					return () -> e.get(f.y);
				} else if (this == Linear) {
					double dx = x - e.get(f.x);
					return () -> e.get(f.y) + dx * e.get(f.findif.dydx());
				}
				throw new IllegalArgumentException("Unsupported Extrapolation method " + this);
			}


		}
	}

}

























