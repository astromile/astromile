package wave.data;

public enum Channels implements Channel{
	Mono(0),
	Left(0),
	Right(1);

	private final int idx;

	private Channels(int idx) {
		this.idx = idx;
	}

	public int getIndex() {
		return idx;
	}

	@Override
	public String getName() {
		return toString();
	}
}
