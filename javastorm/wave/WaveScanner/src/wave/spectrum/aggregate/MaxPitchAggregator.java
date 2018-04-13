package wave.spectrum.aggregate;

import wave.note.Bitch;
import wave.spectrum.SpectrumPoint;

import java.util.List;

public class MaxPitchAggregator extends AbstractPitchAggregator {
	protected MaxPitchAggregator(List<Bitch> bitches, Interval.Generator boundaryGenerator) {
		super(bitches, boundaryGenerator);
	}

	public static MaxPitchAggregator of(List<Bitch> bitches, Interval.Generator boundaryGenerator) {
		return new MaxPitchAggregator(bitches, boundaryGenerator);
	}

	@Override
	protected SpectrumPoint aggregate(List<SpectrumPoint> points, Bitch bitch) {
		return SpectrumPoint.of(bitch.frequency(),
							points.stream().mapToDouble(SpectrumPoint::amplitude).max().orElse(0.));
	}
}
