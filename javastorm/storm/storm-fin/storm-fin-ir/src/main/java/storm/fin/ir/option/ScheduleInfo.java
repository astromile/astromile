package storm.fin.ir.option;

import storm.fin.time.*;

import java.time.*;

public final class ScheduleInfo {
	private final DateInterval interval;
	private final Period period;
	private final StubInfo stub;

	private ScheduleInfo(DateInterval interval, Period period, StubInfo stub) {
		this.interval = interval;
		this.period = period;
		this.stub = stub;
	}

	public static ScheduleInfo of(DateInterval interval, Period period, StubInfo stub) {
		return new ScheduleInfo(interval, period, stub);
	}

	public DateInterval getInterval() {
		return interval;
	}

	public Period getPeriod() {
		return period;
	}

	public StubInfo getStub() {
		return stub;
	}
}
