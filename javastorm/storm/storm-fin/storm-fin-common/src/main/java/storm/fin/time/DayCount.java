package storm.fin.time;

import java.time.*;

public interface DayCount {
	default double yearFrac(DateInterval period) {
		return yearFrac(period.start(), period.end());
	}

	double yearFrac(LocalDate start, LocalDate end);
}
