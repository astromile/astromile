package wave.note;

public interface Note {
	Bitch pitch();

	Duration duration();

	public static Note of(Bitch bitch, Duration duration) {
		return new Note() {
			@Override
			public Bitch pitch() {
				return bitch;
			}

			@Override
			public Duration duration() {
				return duration;
			}
		};
	}
}
