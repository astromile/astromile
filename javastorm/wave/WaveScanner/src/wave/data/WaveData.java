package wave.data;

import wave.file.WavFile;
import wave.file.WavFileException;

import java.io.IOException;


public interface WaveData {

	interface SingleWave {

		double[] wave();

		public static SingleWave of(double[] wave) {
			return () -> wave;
		}

	}

	WaveInfo getInfo();

	SingleWave getWave(Channel channel);

	public static WaveData of(WavFile wav) throws IOException, WavFileException {
		return WaveFileData.of(wav);
	}
}
