package storm.fin.ir.option;


import storm.fin.ir.*;

public final class CapFloorInfo implements Option {

	public enum Type {
		Cap(OptionType.Call), Floor(OptionType.Put);

		private final OptionType optionType;

		Type(OptionType optionType) {this.optionType = optionType;}

		public OptionType getOptionType() {return optionType;}
	}

	private final ScheduleInfo schedule;
	private final Libor index;
	private final double strike;
	private final Type type;

	public CapFloorInfo(ScheduleInfo schedule, Libor index, double strike, Type type) {
		this.schedule = schedule;
		this.index = index;
		this.strike = strike;
		this.type = type;
	}

	@Override
	public OptionType getOptionType() {
		return type.getOptionType();
	}

	public ScheduleInfo getSchedule() {
		return schedule;
	}

	public Libor getIndex() {
		return index;
	}

	public double getStrike() {
		return strike;
	}

	public Type getType() {
		return type;
	}
}
