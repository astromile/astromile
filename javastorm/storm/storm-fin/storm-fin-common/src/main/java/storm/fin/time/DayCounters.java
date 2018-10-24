package storm.fin.time;

import java.time.*;
import java.util.function.*;

public enum DayCounters implements DayCount {
	Act360(days -> days / 360.),
	Act365(days -> days / 365.),
	Act365_25(days -> days / 365.25);

	private final Function<Long, Double> impl;

	DayCounters(Function<Long, Double> impl) {
		this.impl = impl;
	}

	@Override
	public double yearFrac(DateInterval interval) {
		return impl.apply(interval.days());
	}

	@Override
	public double yearFrac(LocalDate start, LocalDate end) {
		return impl.apply(DateInterval.days(start, end));
	}

}
