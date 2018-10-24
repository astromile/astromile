package storm.fin.time;

import java.time.*;

public final class StartEnd implements DateInterval {

	public static StartEnd of(LocalDate start, LocalDate end) {
		return new StartEnd(start, end);
	}

	public static StartEnd of(LocalDate start, Period period) {
		return new StartEnd(start, start.plus(period));
	}

	private final LocalDate start;
	private final LocalDate end;

	private StartEnd(LocalDate start, LocalDate end) {
		this.start = start;
		this.end = end;
	}

	public LocalDate start() {
		return start;
	}

	public LocalDate end() {
		return end;
	}

}
