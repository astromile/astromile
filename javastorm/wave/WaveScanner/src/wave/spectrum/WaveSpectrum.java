package wave.spectrum;

import wave.util.Ensure;

import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collector;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public interface WaveSpectrum {

	List<SpectrumPoint> points();

	static WaveSpectrum of(double[] frequencies, double[] amplitudes) {
		Objects.requireNonNull(frequencies, "Frequencies");
		Objects.requireNonNull(amplitudes, "Amplitudes");
		Ensure.that(frequencies.length == amplitudes.length, () ->
							"nb of frequencies " + frequencies.length
												+ " does not match nb of amplitudes " + amplitudes.length);
		return of(IntStream.range(0,frequencies.length)
							.mapToObj(i->SpectrumPoint.of(frequencies[i],amplitudes[i]))
							.collect(Collectors.toList()));
	}

	static WaveSpectrum of(List<SpectrumPoint> points) {
		return new WaveSpectrum() {
			@Override
			public List<SpectrumPoint> points() {
				return points;
			}
		};
	}

}
