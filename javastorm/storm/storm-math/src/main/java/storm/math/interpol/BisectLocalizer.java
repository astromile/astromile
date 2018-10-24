package storm.math.interpol;

import java.util.*;

public class BisectLocalizer implements Localizer {
	@Override
	public int getIntervalIndex(double x, double[] points) {
		return Arrays.binarySearch(points, x);
	}

}
