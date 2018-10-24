package storm.fin.time;

import java.time.*;

public interface DateRoll {
	LocalDate roll(LocalDate date, BusinessCalendar calendar);
}
