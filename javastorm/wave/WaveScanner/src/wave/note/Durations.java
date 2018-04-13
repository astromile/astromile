package wave.note;

public enum Durations implements Duration {
	Whole(1), Half(2), Quarter(4), Eighth(8), Sixteenth(16), ThirtySecond(32), SixtyFourth(64), HundredTwentyEighth(128);

	private final int frequency;

	Durations(int frequency) {
		this.frequency = frequency;
	}

	@Override
	public double seconds() {
		return 1./frequency;
	}
}
