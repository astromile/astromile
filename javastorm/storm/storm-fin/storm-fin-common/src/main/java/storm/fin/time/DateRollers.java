package storm.fin.time;

import storm.fin.com.*;

import java.time.*;

public enum DateRollers implements DateRoll {
	Unadjusted((date, calendar) -> date),
	Following((date, calendar) -> moveToBusiness(Direction.Forward, date, calendar)),
	Preceding((date, calendar) -> moveToBusiness(Direction.Backward, date, calendar)),
	ModifiedFollowing((date, calendar) -> moveToBusinessSameMonth(Direction.Forward, date, calendar)),
	ModifiedPreceding((date, calendar) -> moveToBusinessSameMonth(Direction.Backward, date, calendar));

	private final DateRoll impl;

	DateRollers(DateRoll impl) {this.impl = impl;}

	public static DateRollers directional(Direction direction) {
		switch (direction) {
			case Forward:
				return Following;
			case Backward:
				return Preceding;
			default:
				return Unadjusted;
		}
	}

	public static DateRollers modified(Direction direction) {
		switch (direction) {
			case Forward:
				return ModifiedFollowing;
			case Backward:
				return ModifiedPreceding;
			default:
				return Unadjusted;
		}
	}

	@Override
	public LocalDate roll(LocalDate date, BusinessCalendar calendar) {
		return impl.roll(date, calendar);
	}

	private static LocalDate moveToBusinessSameMonth(Direction direction,
	                                                 LocalDate date, BusinessCalendar calendar) {
		LocalDate busDate = moveToBusiness(direction, date, calendar);
		return busDate.getMonth() == date.getMonth() ? busDate :
		       moveToBusiness(direction.opposite(), date, calendar);
	}

	private static LocalDate moveToBusiness(Direction direction,
	                                        LocalDate date, BusinessCalendar calendar) {
		while (!calendar.isBusinessDay(date)) {
			date = date.plusDays(direction.getValue());
		}
		return date;
	}
}
