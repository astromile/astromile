package wave.data;

public interface Channel {
	int getIndex();

	String getName();

	public static Channel of(int channel, int nbOfChannels) {
		if (nbOfChannels == 1) {
			return Channels.Mono;
		} else if (nbOfChannels == 2) {
			return channel == 0 ? Channels.Left : Channels.Right;
		} else {
			return new Channel() {
				@Override
				public int getIndex() {
					return channel;
				}

				@Override
				public String getName() {
					return String.valueOf(channel);
				}
			};
		}
	}
}
