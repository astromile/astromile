package wave.note;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public enum Octaves implements Octave {
	SubContraOctave(0),
	ContraOctave(1),
	GreatOctave(2),
	SmallOctave(3),
	FirstOctave(4),
	SecondOctave(5),
	ThirdOctave(6),
	FourthOctave(7),
	FifthOctave(8);

	private final int index;
	private final List<Bitch> bitches;

	Octaves(int index) {
		this.index = index;
		EquitemporedBitch.Factory factory = EquitemporedBitch.Factory.INSTANCE;
		bitches = IntStream.range(0, EquitemporedBitch.OCTAVE_SIZE)
							.mapToObj(gammaNote ->
												factory.forStep((index - 5)
																	* EquitemporedBitch.OCTAVE_SIZE + gammaNote - 9))
							.collect(Collectors.toList());
	}

	@Override
	public int getIndex() {
		return index;
	}

	@Override
	public String getName() {
		return toString();
	}

	@Override
	public List<Bitch> getBitches() {
		return bitches;
	}
}
