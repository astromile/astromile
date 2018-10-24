package storm.fin.ir.swap;

import storm.fin.time.*;

import java.time.*;

public interface Coupon {

	DateInterval

	LocalDate payDate();

	double yearFrac();

	Rate rate();
}
