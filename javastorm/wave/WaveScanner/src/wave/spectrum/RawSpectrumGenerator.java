package wave.spectrum;

import org.apache.commons.math3.complex.Complex;
import org.apache.commons.math3.transform.DftNormalization;
import org.apache.commons.math3.transform.FastFourierTransformer;
import org.apache.commons.math3.transform.TransformType;
import wave.data.Channel;
import wave.data.WaveData;
import wave.data.WaveInfo;

import java.util.Arrays;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class RawSpectrumGenerator extends AbstractSpectrumGenerator {

	private RawSpectrumGenerator(
						WaveInfo waveInfo, WaveData.SingleWave wave) {
		super(waveInfo, wave);
	}

	public static RawSpectrumGenerator of(
						WaveInfo waveInfo, WaveData.SingleWave wave) {
		return new RawSpectrumGenerator(waveInfo, wave);
	}

	public static RawSpectrumGenerator of(WaveData wav, Channel channel) {
		return new RawSpectrumGenerator(wav.getInfo(), wav.getWave(channel));
	}

	@Override
	public WaveSpectrum generate(TimeWindow window) {
		int start = window.getStartIndex(getInfo());
		int end = window.getEndIndex(getInfo());
		return WaveSpectrum.of(generateFrequencies(end - start), generateAmplitudes(start, end));
	}

	private double[] generateAmplitudes(int start, int end) {
		FastFourierTransformer fft = new FastFourierTransformer(DftNormalization.STANDARD);
		double[] wave = getSubWave(start, end);
		if (wave.length == 0) return wave;
		return extractAmplitudes(fft.transform(wave, TransformType.FORWARD), end - start);
	}

	private double[] extractAmplitudes(Complex[] magnitudes, int sz) {
		double scale = 2. / getInfo().getFrameRate();
		double[] amplitudes = new double[sz];
		IntStream.range(0, sz).forEach(i -> amplitudes[i] = scale * magnitudes[i].abs());
		return amplitudes;
	}

	private double[] getSubWave(int start, int end) {
		WaveData.SingleWave w = getWave();
		int fftSize = getFFTSize(end - start);
		double[] wave = new double[fftSize];
		IntStream.range(0, end - start).forEach(i -> wave[i] = w.wave()[start + i]);
		return wave;
	}

	private double[] generateFrequencies(int n) {
		double[] freq = new double[n];
		IntStream.rangeClosed(1, n).forEach(i ->
							freq[i - 1] = (i - 1.) * getInfo().getFrameRate() / getFFTSize(n));
		return freq;
	}


}
