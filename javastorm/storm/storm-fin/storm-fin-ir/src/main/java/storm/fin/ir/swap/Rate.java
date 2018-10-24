package storm.fin.ir.swap;

import storm.com.*;
import storm.fin.ir.*;

import java.time.*;

public interface Rate {
	DoubleValue value(RateMarket market);

	static Rate fixed(double fixedRate) {
		return market -> () -> fixedRate;
	}

	static Rate libor(LocalDate fixingDate, Libor libor) {
		return market -> market.rate(fixingDate, libor);
	}

	static Rate linear(Rate rate, Linear linear) {
		return market -> {
			DoubleValue rateValue = rate.value(market);
			return () -> linear.apply(rateValue.get());
		};
	}
}
