package storm.fin.ir;

import storm.fin.com.*;
import storm.fin.ir.*;
import storm.fin.time.*;

import java.time.*;
import java.util.*;

public enum Libors implements Libor {
	Euribor1m(Families.Euribor, Period.ofMonths(1)),
	Euribor3m(Families.Euribor, Period.ofMonths(3)),
	Euribor6m(Families.Euribor, Period.ofMonths(6)),
	Euribor12m(Families.Euribor, Period.ofMonths(12)),
	USDLibor1m(Families.USDLibor, Period.ofMonths(1)),
	USDLibor3m(Families.USDLibor, Period.ofMonths(3)),
	USDLibor6m(Families.USDLibor, Period.ofMonths(6)),
	USDLibor12m(Families.USDLibor, Period.ofMonths(12));

	private final Family family;
	private final Period tenor;

	Libors(Family family, Period tenor) {
		this.family = family;
		this.tenor = tenor;
	}

	@Override
	public Family family() {
		return family;
	}

	@Override
	public Period tenor() {
		return tenor;
	}

	public enum Families implements Family {
		Euribor(BusinessCalendar.TARGET, Ccy.EUR, DayCounters.Act360, DateRollers.ModifiedFollowing),
		USDLibor(BusinessCalendar.USA, Ccy.USD, DayCounters.Act360, DateRollers.ModifiedFollowing);

		private final BusinessCalendar calendar;
		private final Currency currency;
		private final DayCount dayCount;
		private final DateRoll dateRoll;
		private final int fixingLag;

		/**
		 * default ctor with {@code fixingLag=2}
		 */
		Families(BusinessCalendar calendar, Currency currency, DayCount dayCount, DateRoll dateRoll) {
			this(calendar, currency, dayCount, dateRoll, 2);
		}

		Families(BusinessCalendar calendar, Currency currency, DayCount dayCount, DateRoll dateRoll,
		         int fixingLag) {
			this.calendar = calendar;
			this.currency = currency;
			this.dayCount = dayCount;
			this.dateRoll = dateRoll;
			this.fixingLag = fixingLag;
		}

		@Override
		public BusinessCalendar calendar() {
			return calendar;
		}

		@Override
		public Currency currency() {
			return currency;
		}

		@Override
		public DayCount dayCount() {
			return dayCount;
		}

		@Override
		public DateRoll dateRoll() {
			return dateRoll;
		}

		@Override
		public int fixingLag() {
			return fixingLag;
		}
	}
}
