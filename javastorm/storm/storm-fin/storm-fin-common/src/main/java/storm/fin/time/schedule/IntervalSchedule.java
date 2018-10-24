package storm.fin.time.schedule;

import storm.fin.time.*;

import java.time.*;
import java.util.*;

public interface IntervalSchedule extends Schedule {
	default DateInterval interval(int i) {
		List<LocalDate> dates = dates();
		return DateInterval.of(dates.get(i), dates.get(i + 1));
	}

	default int intervals() {
		return Math.max(0, size() - 1);
	}

}
