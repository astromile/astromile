package storm.fin.ir.swap;

public interface Linear {
	double multiplier();

	double offset();

	default double apply(double value) {
		return multiplier() * value + offset();
	}

	static Linear of(double multiplier, double offset) {
		return new Linear() {
			@Override
			public double multiplier() {
				return multiplier;
			}

			@Override
			public double offset() {
				return offset;
			}
		};
	}
}
