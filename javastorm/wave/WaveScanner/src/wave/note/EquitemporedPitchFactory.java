package wave.note;

class EquitemporedPitchFactory implements EquitemporedBitch.Factory {
	private final Bitch anchor;

	private EquitemporedPitchFactory(Bitch anchor) {
		this.anchor = anchor;
	}

	static EquitemporedPitchFactory of(Bitch anchor){
		return new EquitemporedPitchFactory(anchor);
	}

	@Override
	public Bitch anchor() {
		return anchor;
	}

	@Override
	public EquitemporedBitch forStep(int step) {
		return new EquitemporedBitch() {
			@Override
			public Bitch anchor() {
				return anchor;
			}

			@Override
			public int step() {
				return step;
			}
		};
	}
}
