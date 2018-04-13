package wave.data;

import wave.file.WavFile;
import wave.file.WavFileException;
import wave.util.Ensure;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class WaveFileData implements WaveData {

	private final String fileName;
	private final WaveInfo info;
	private final List<SingleWave> channels;

	public WaveFileData(String fileName, WaveInfo waveInfo, List<SingleWave> channels) {
		this.fileName=fileName;
		this.channels = channels;
		info = waveInfo;
	}

	public String getFileName(){
		return fileName;
	}

	@Override
	public SingleWave getWave(Channel channel) {
		return channels.get(channel.getIndex());
	}

	@Override
	public WaveInfo getInfo() {
		return info;
	}

	public static WaveData of(WavFile wav) throws IOException, WavFileException {
		Ensure.that(wav.getNumFrames() <= Integer.MAX_VALUE,
							() -> "Number of frames " + wav.getNumFrames()
												+ " exceeds maximum of " + Integer.MAX_VALUE);
		Ensure.that(wav.getSampleRate() <= Integer.MAX_VALUE,
							() -> "Frame rate " + wav.getNumFrames()
												+ " exceeds maximum of " + Integer.MAX_VALUE);

		WaveInfo waveInfo = WaveInfo.of(
							wav.getNumChannels(), (int) wav.getNumFrames(), (int) wav.getSampleRate());
		return new WaveFileData(wav.getFileName(), waveInfo, readChannels(wav));
	}


	private static List<SingleWave> readChannels(WavFile wav) throws IOException, WavFileException {
		int nbOfChannels = wav.getNumChannels();
		if (wav.getNumFrames() > Integer.MAX_VALUE) {
			throw new IOException("Number of frames " + wav.getNumFrames()
								+ " exceeds maximum of " + Integer.MAX_VALUE);
		}
		int nbOfFrames = (int) wav.getNumFrames();
		double[][] buffer = new double[nbOfChannels][nbOfFrames];
		wav.readFrames(buffer, nbOfFrames);
		return IntStream.range(0, nbOfChannels)
							.mapToObj(i -> SingleWave.of(buffer[i]))
							.collect(Collectors.toList());
	}
}
