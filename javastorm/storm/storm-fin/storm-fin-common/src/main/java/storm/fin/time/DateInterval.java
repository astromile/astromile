package storm.fin.time;

import java.time.*;

public interface DateInterval {

	LocalDate start();

	LocalDate end();

	static DateInterval of(LocalDate start, LocalDate end) {
		return new DateInterval() {
			@Override
			public LocalDate start() { return start; }

			@Override
			public LocalDate end() { return end; }
		};
	}

	static DateInterval of(LocalDate start, Period period) {
		return of(start, start.plus(period));
	}

	default long days() {
		return days(start(), end());
//		long days = Duration.between(start(), end()).toDays();
//		Assure.that(days < Integer.MAX_VALUE,
//		            () -> "Date Interval is too long: " + days + " days");
//		return (int) days;
	}

	static long days(LocalDate start, LocalDate end) {
		return Duration.between(start, end).toDays();
	}

//	default double yearFrac(DayCounter dc) {
//		return dc.coverage(start(), end());
//	}
}
