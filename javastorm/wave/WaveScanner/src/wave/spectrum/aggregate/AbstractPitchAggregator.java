package wave.spectrum.aggregate;

import wave.note.Bitch;
import wave.spectrum.SpectrumPoint;
import wave.spectrum.WaveSpectrum;
import wave.util.Ensure;

import java.util.List;
import java.util.stream.Collectors;

abstract class AbstractPitchAggregator implements PitchAggregator {
	private final List<Bitch> bitches;
	private final Interval.Generator boundaryGenerator;

	protected AbstractPitchAggregator(List<Bitch> bitches, Interval.Generator boundaryGenerator) {
		this.bitches = bitches;
		this.boundaryGenerator=boundaryGenerator;
	}

	@Override
	public List<Bitch> getBitches() {
		return bitches;
	}

	@Override
	public WaveSpectrum aggregate(WaveSpectrum rawSpectrum) {
		List<Interval> boundaries = boundaryGenerator.generate(rawSpectrum.points());
		Ensure.that(boundaries.size()== bitches.size(), ()->"Boundaries size " + boundaries.size()
												+ " does not match bitches size " + bitches.size());
		List<SpectrumPoint> rawPoints = rawSpectrum.points();
		List<SpectrumPoint> pitchPoints = boundaries.stream()
							.map(b -> aggregate(rawPoints.subList(b.start(),b.end()),b.pitch()))
							.collect(Collectors.toList());
		return WaveSpectrum.of(pitchPoints);
	}

	protected abstract SpectrumPoint aggregate(List<SpectrumPoint> points, Bitch bitch);
}
