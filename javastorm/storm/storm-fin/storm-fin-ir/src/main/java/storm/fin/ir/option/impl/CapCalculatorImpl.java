package storm.fin.ir.option.impl;


import storm.fin.ir.curve.*;
import storm.fin.ir.option.*;

import java.util.function.*;

//@Remote
public class CapCalculatorImpl implements CapCalculator {

	private Curves curves;
	private CapletSurface capletSurface;

	public void updateCurves(/*@Observes*/ Curves curves) {
		this.curves = curves;
	}

	@Override
	public Result calculate(CapFloorInfo cap) {
		return null;
	}

	@Override
	public void subscribe(CapFloorInfo cap, Consumer<Result> consumer) {

	}
}
