package storm.math;

import storm.com.*;

import java.util.function.*;

public final class Doubles {

	static public double[] operate(double[] x, double[] y, DoubleBinaryOperator operator) {
		Assure.sameSize(x, y, () -> "arguments of element-wise binary vector operator");
		double[] result = new double[x.length];
		for (int i = 0; i < x.length; ++i) {
			result[i] = operator.applyAsDouble(x[i], y[i]);
		}
		return result;
	}

}
