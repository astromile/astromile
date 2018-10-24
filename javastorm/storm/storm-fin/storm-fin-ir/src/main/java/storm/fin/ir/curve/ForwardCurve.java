package storm.fin.ir.curve;

import storm.com.*;
import storm.fin.ir.*;
import storm.fin.time.*;

public interface ForwardCurve {

	ForwardRate forwardRate(DateInterval period, DayCount dayCount);

	static ForwardCurve of(DiscountCurve discountCurve) {
		return (period, dayCount) -> {
			double delta = dayCount.yearFrac(period);
			DoubleValue dfStart = discountCurve.discountFactor(period.start());
			DoubleValue dfEnd = discountCurve.discountFactor(period.end());
			return () -> (dfStart.get() / dfEnd.get() - 1.) / delta;
		};
	}

}
