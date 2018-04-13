package wave.data;

public interface WaveInfo {

	int getNbOfChannels();

	int getNbOfFrames();

	int getFrameRate();

	default double getDuration() {
		return (double) getNbOfFrames() / getFrameRate();
	}

	static WaveInfo of(int nbOfChannels, int nbOfFrames, int frameRate) {
		return new WaveInfo() {
			@Override
			public int getNbOfChannels() {
				return nbOfChannels;
			}

			@Override
			public int getNbOfFrames() {
				return nbOfFrames;
			}

			@Override
			public int getFrameRate() {
				return frameRate;
			}
		};
	}

}
