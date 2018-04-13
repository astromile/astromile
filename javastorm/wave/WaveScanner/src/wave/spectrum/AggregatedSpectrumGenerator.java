package wave.spectrum;

import wave.note.Bitch;
import wave.spectrum.aggregate.Interval;
import wave.spectrum.aggregate.MaxPitchAggregator;
import wave.spectrum.aggregate.SimpleIntervalGenerator;

import java.util.List;

public class AggregatedSpectrumGenerator implements SpectrumGenerator {
	public interface Aggregator {
		WaveSpectrum aggregate(WaveSpectrum rawSpectrum);
	}

	private final RawSpectrumGenerator rawSpectrumGenerator;
	private final Aggregator aggregator;

	private AggregatedSpectrumGenerator(
						RawSpectrumGenerator rawSpectrumGenerator, Aggregator aggregator) {
		this.rawSpectrumGenerator = rawSpectrumGenerator;
		this.aggregator = aggregator;
	}

	public static AggregatedSpectrumGenerator of
						(RawSpectrumGenerator rawSpectrumGenerator, Aggregator aggregator) {
		return new AggregatedSpectrumGenerator(rawSpectrumGenerator, aggregator);
	}

	public static AggregatedSpectrumGenerator ofMaximum(
						RawSpectrumGenerator rawSpectrumGenerator, List<Bitch> bitches) {
		return of(rawSpectrumGenerator,
							MaxPitchAggregator.of(bitches, SimpleIntervalGenerator.of(bitches)));
	}

	@Override
	public WaveSpectrum generate(TimeWindow window) {
		WaveSpectrum rawSpectrum = rawSpectrumGenerator.generate(window);
		return aggregator.aggregate(rawSpectrum);
	}
}
