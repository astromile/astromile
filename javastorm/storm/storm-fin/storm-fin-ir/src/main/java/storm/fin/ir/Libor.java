package storm.fin.ir;

import storm.fin.time.*;

import java.time.*;
import java.util.*;

public interface Libor {
	Family family();

	Period tenor();

	interface Family {
		Currency currency();

		BusinessCalendar calendar();

		DateRoll dateRoll();

		DayCount dayCount();

		int fixingLag();

	}

	default DateInterval period(LocalDate fixingDate) {
		Family f = family();
		LocalDate start = f.calendar().skip(f.fixingLag(), fixingDate);
		LocalDate end = f.dateRoll().roll(start.plus(tenor()), f.calendar());
		return DateInterval.of(start, end);
	}
}
