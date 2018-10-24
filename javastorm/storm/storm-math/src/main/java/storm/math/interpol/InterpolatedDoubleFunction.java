package storm.math.interpol;

import storm.com.*;

public interface InterpolatedDoubleFunction {
	DoubleValue interpolate(double x);
}
