package wave.note;

import java.util.Optional;

public interface EquitemporedBitch extends Bitch {
	static final int OCTAVE_SIZE = 12;
	static final double OCTAVE_FACTOR = 2.0;
	static final double HALFTONE_FACTOR = Math.pow(OCTAVE_FACTOR, 1.0 / OCTAVE_FACTOR);

	Bitch anchor();

	int step();

	static boolean equals(EquitemporedBitch bitch1, EquitemporedBitch bitch2) {
		if(bitch1==null || bitch2==null){
			return false;
		}
		return bitch1.anchor()==bitch2.anchor() && bitch1.step()==bitch2.step();
	}

	default String scientificNotation(){
		return Optional.ofNullable(Bitches.of(this)).map(Bitches::toString)
							.orElse(anchor()+"Hz " + (step()>=0 ? "+ " : "- ")  + step() + " half tones");
	}

	@Override
	default double frequency() {
		return anchor().frequency() * Math.pow(OCTAVE_FACTOR, (double) step() / OCTAVE_SIZE);
	}

	static EquitemporedBitch fromString(String bitch) {
		return Bitches.valueOf(bitch.toUpperCase());
	}

	interface Factory {
		Bitch anchor();

		EquitemporedBitch forStep(int step);

		static final Factory INSTANCE = of(Bitch.of(440.));

		static Factory of(Bitch anchor) {
			return EquitemporedPitchFactory.of(anchor);
		}
	}
}
