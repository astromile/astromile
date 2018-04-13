package wave.note;

public interface Bitch {
	double frequency();
	static Bitch of(double frequency){
		return new Bitch() {
			@Override
			public double frequency() {
				return frequency;
			}
		};
	}
}
