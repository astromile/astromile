package storm.fin.ir.curve;

import storm.com.*;
import storm.fin.ir.*;
import storm.fin.time.*;

import java.time.*;

public interface DiscountCurve {

	DiscountFactor discountFactor(LocalDate date);

	/**
	 * creates discount curve with ACT/365.25 assumption
	 */
	static DiscountCurve of(ZeroCurve zeroCurve, LocalDate horizon) {
		return of(zeroCurve, horizon, DayCounters.Act365_25);
	}

	static DiscountCurve of(ZeroCurve zeroCurve, LocalDate horizon, DayCount dc) {
		return date -> {
			double time = dc.yearFrac(horizon, date);
			DoubleValue zeroRate = zeroCurve.zeroRate(date);
			return () -> Math.exp(-time * zeroRate.get());
		};
	}
}
