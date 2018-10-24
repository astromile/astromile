package storm.fin.ir.curve.calib;

import java.math.*;

public interface Quote {
	BigDecimal value();

	Info info();

	enum Type {
		Depo, FRA, Swap
	}

	interface Info {
		Type type();
	}
}
