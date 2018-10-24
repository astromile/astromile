package storm.fin.ir.curve.calib;

import storm.fin.ir.curve.*;

import java.util.*;

public interface CurveCalibrator {

	Result calibrate(List<Quote> quotes);

	interface Result {
		ZeroCurve curve();
	}

}
