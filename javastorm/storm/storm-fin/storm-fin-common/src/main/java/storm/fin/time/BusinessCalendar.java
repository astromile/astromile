package storm.fin.time;

import storm.fin.com.*;

import java.time.*;

public interface BusinessCalendar {
	boolean isBusinessDay(LocalDate date);

	default LocalDate skip(int nbOfDays, LocalDate fromDate) {
		Direction direction = Direction.of(nbOfDays);
		DateRollers dateRoll = DateRollers.directional(Direction.of(nbOfDays));
		while (nbOfDays > 0) {
			fromDate = dateRoll.roll(fromDate.plusDays(direction.getValue()), this);
			nbOfDays -= direction.getValue();
		}
		return fromDate;
	}

	BusinessCalendar ALLDAYS = date -> true;
	BusinessCalendar NOWEEKENDS = date -> date.getDayOfWeek().getValue() < 6;

	interface Provider {
		BusinessCalendar calendar(String name);
	}

	static Provider PROVIDER = name -> {
		name = name.toUpperCase();
		switch (name) {
			case "ALL":
			case "ALL DAYS":
			case "ALLDAYS":
			case "ALL_DAYS":
				return ALLDAYS;
			case "TARGET":
				return NOWEEKENDS; // TODO implement TARGET calendar
			case "USA":
				return NOWEEKENDS; // TODO implement USA calendar
			default:
				return NOWEEKENDS;
		}
	};

	BusinessCalendar TARGET = PROVIDER.calendar("TARGET");
	BusinessCalendar USA = PROVIDER.calendar("USA");
}
