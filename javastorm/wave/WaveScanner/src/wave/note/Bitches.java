package wave.note;

import java.util.Arrays;

public enum Bitches implements Bitch, EquitemporedBitch {
	C3(-21), Db3(-20), D3(-19), Eb3(-18), E3(-17), F3(-16), Gb3(-15), G3(-14), Ab3(-13), A3(-12), Hb3(-11), H3(-10),
	C4(-9), Db4(-8), D4(-7), Eb4(-6), E4(-5), F4(-4), Gb4(-3), G4(-2), Ab4(-1), A4(0), Hb4(1), H4(2),
	C5(3), Db5(4), D5(5), Eb5(6), E5(7), F5(8), Gb5(9), G5(10), Ab5(11), A5(12), Hb5(13), H5(14),
	C6(15), Db6(16), D6(17), Eb6(18), E6(19), F6(20), Gb6(21), G6(22), Ab6(23), A6(24), Hb6(25), H6(26);

	private final EquitemporedBitch pitch;

	public static Bitches of(EquitemporedBitch bitch) {
		return Arrays.stream(values()).filter(b -> EquitemporedBitch.equals(b,bitch)).findAny()
							.orElse(null);
	}

	Bitches(int step) {
		pitch = EquitemporedBitch.Factory.INSTANCE.forStep(step);
	}

	@Override
	public double frequency() {
		return pitch.frequency();
	}

	@Override
	public int step() {
		return pitch.step();
	}

	public Bitch anchor() {
		return Factory.INSTANCE.anchor();
	}
}
