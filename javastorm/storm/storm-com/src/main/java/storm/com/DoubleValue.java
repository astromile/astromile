package storm.com;

import java.util.function.*;

public interface DoubleValue extends DoubleSupplier {

	double get();

	@Override
	default double getAsDouble() {
		return get();
	}
}
