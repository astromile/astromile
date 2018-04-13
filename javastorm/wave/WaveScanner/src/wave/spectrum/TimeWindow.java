package wave.spectrum;

import wave.data.WaveData;
import wave.data.WaveInfo;

public interface TimeWindow {
	double start();

	double end();

	default int getStartIndex(WaveInfo waveInfo) {
		int start = (int) Math.ceil(start() * waveInfo.getFrameRate());
		return Math.max(0, Math.min(start, waveInfo.getNbOfFrames()));
	}

	default int getEndIndex(WaveInfo waveInfo) {
		int end = (int) Math.floor(end() * waveInfo.getFrameRate()) + 1;
		return Math.min(waveInfo.getNbOfFrames(), Math.max(0, end));
	}

	static TimeWindow of(double start, double end) {
		return new TimeWindow() {
			@Override
			public double start() {
				return start;
			}

			@Override
			public double end() {
				return end;
			}
		};
	}

	static TimeWindow of(int startIdx, int endIdx, WaveInfo waveInfo) {
		double start = (double) Math.max(0, startIdx) / waveInfo.getFrameRate();
		double end = (Math.min(endIdx, waveInfo.getNbOfFrames()) - 0.5) / waveInfo.getFrameRate();
		return of(start, end);
	}
}
