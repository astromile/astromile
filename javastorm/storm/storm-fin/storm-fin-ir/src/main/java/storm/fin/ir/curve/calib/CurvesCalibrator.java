package storm.fin.ir.curve.calib;

import storm.fin.ir.*;
import storm.fin.ir.curve.*;

import java.util.*;

public interface CurvesCalibrator {

	Result calibrate(Map<Libor, List<Quote>> quotes, Libor discountIndex);

	interface Result {

		Curves curves();

	}

}
