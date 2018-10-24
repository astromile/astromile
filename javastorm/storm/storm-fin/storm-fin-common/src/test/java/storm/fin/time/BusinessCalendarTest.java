package storm.fin.time;

import org.junit.*;

import java.time.*;

import static org.junit.Assert.*;

public class BusinessCalendarTest {

	@Test
	public void testNoWeekendsCalendar() {
		BusinessCalendar calendar = BusinessCalendar.NOWEEKENDS;
		LocalDate today = LocalDate.of(2018, Month.JULY, 14); /* Sat */
		assertEquals(DayOfWeek.SATURDAY, today.getDayOfWeek());
		assertFalse(calendar.isBusinessDay(today));
		LocalDate monday20180716 = calendar.skip(1, today);
		assertEquals(monday20180716, LocalDate.of(2018, Month.JULY, 16));
		LocalDate tuesday20180717 = calendar.skip(2, today);
		/* parents in law comes to visit us :) */
		assertEquals(tuesday20180717, LocalDate.of(2018, Month.JULY, 17));
	}

}