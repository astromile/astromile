package storm.fin.ir.swap;

import storm.fin.time.*;

import java.time.*;

public interface Coupon {

	DateInterval interval();

	LocalDate payDate();

	double yearFrac();

	Rate rate();
}
