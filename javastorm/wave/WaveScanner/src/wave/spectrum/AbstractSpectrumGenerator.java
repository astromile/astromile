package wave.spectrum;

import wave.data.WaveData;
import wave.data.WaveInfo;

public abstract class AbstractSpectrumGenerator implements SpectrumGenerator {
	private final WaveInfo waveInfo;
	private final WaveData.SingleWave wave;

	protected AbstractSpectrumGenerator(WaveInfo waveInfo, WaveData.SingleWave wave) {
		this.waveInfo = waveInfo;
		this.wave = wave;
	}

	protected WaveInfo getInfo() {
		return waveInfo;
	}

	protected static int getFFTSize(int n) {
		return (int) Math.pow(2., (int) Math.ceil(Math.log(n) / Math.log(2.)));
	}

	protected WaveData.SingleWave getWave() {
		return wave;
	}

}
