package storm.fin.time;

import org.junit.*;
import storm.fin.com.*;

import java.time.*;

import static org.junit.Assert.*;

public class DateRollersTest {

	@Test
	public void roll_Unadjusted() {
		DateRollers unadjusted = DateRollers.directional(Direction.Undefined);
		LocalDate today = LocalDate.of(2018, Month.JULY, 14);
		BusinessCalendar calendar = BusinessCalendar.NOWEEKENDS;
		assertEquals(DateRollers.Unadjusted, unadjusted);
		assertEquals(DayOfWeek.SATURDAY, today.getDayOfWeek());
		assertEquals(today, unadjusted.roll(today, calendar));
		assertEquals(today.plusDays(2), unadjusted.roll(today.plusDays(2), calendar));
	}

	@Test
	public void roll_Following() {
		DateRollers following = DateRollers.directional(Direction.Forward);
		assertEquals(DateRollers.Following, following);
		LocalDate today = LocalDate.of(2018, Month.JULY, 14);
		BusinessCalendar calendar = BusinessCalendar.NOWEEKENDS;
		assertEquals(today.plusDays(2), following.roll(today, calendar));
		assertEquals(today.plusDays(2), following.roll(today.plusDays(2), calendar));
		LocalDate endOfMonth = LocalDate.of(2018, Month.JUNE, 30);
		assertEquals(DayOfWeek.SATURDAY, endOfMonth.getDayOfWeek());
		assertEquals(endOfMonth.plusDays(2), following.roll(endOfMonth, calendar));
	}

	@Test
	public void roll_Preceding() {
		DateRollers preceding = DateRollers.directional(Direction.Backward);
		assertEquals(DateRollers.Preceding, preceding);
		LocalDate today = LocalDate.of(2018, Month.JULY, 14);
		BusinessCalendar calendar = BusinessCalendar.NOWEEKENDS;
		assertEquals(today.plusDays(-1), preceding.roll(today, calendar));
		assertEquals(today.plusDays(2), preceding.roll(today.plusDays(2), calendar));
		LocalDate startOfMonth = LocalDate.of(2018, Month.JULY, 1);
		assertEquals(DayOfWeek.SUNDAY, startOfMonth.getDayOfWeek());
		assertEquals(startOfMonth.plusDays(-2), preceding.roll(startOfMonth, calendar));
	}

	@Test
	public void roll_ModFollowing() {
		DateRollers modFol = DateRollers.modified(Direction.Forward);
		assertEquals(DateRollers.ModifiedFollowing, modFol);
		LocalDate today = LocalDate.of(2018, Month.JULY, 14);
		BusinessCalendar calendar = BusinessCalendar.NOWEEKENDS;
		assertEquals(today.plusDays(2), modFol.roll(today, calendar));
		assertEquals(today.plusDays(2), modFol.roll(today.plusDays(2), calendar));
		LocalDate endOfMonth = LocalDate.of(2018, Month.JUNE, 30);
		assertEquals(DayOfWeek.SATURDAY, endOfMonth.getDayOfWeek());
		assertEquals(endOfMonth.plusDays(-1), modFol.roll(endOfMonth, calendar));
	}

	@Test
	public void roll_ModPreceding() {
		DateRollers modPre = DateRollers.modified(Direction.Backward);
		assertEquals(DateRollers.ModifiedPreceding, modPre);
		LocalDate today = LocalDate.of(2018, Month.JULY, 14);
		BusinessCalendar calendar = BusinessCalendar.NOWEEKENDS;
		assertEquals(today.plusDays(-1), modPre.roll(today, calendar));
		assertEquals(today.plusDays(2), modPre.roll(today.plusDays(2), calendar));
		LocalDate startOfMonth = LocalDate.of(2018, Month.JULY, 1);
		assertEquals(DayOfWeek.SUNDAY, startOfMonth.getDayOfWeek());
		assertEquals(startOfMonth.plusDays(1), modPre.roll(startOfMonth, calendar));
	}

}