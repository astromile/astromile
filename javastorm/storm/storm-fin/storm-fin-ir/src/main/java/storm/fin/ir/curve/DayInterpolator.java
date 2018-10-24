package storm.fin.ir.curve;

import storm.com.*;

public interface DayInterpolator {
	DoubleValue interpolate(long day);
}
