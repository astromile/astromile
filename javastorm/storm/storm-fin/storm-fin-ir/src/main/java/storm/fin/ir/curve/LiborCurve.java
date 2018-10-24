package storm.fin.ir.curve;

import storm.fin.ir.*;
import storm.fin.time.*;

import java.time.*;

public interface LiborCurve extends ForwardCurve {

	default ForwardRate forwardLibor(LocalDate fixingDate) {
		return forwardRate(libor().period(fixingDate), libor().family().dayCount());
	}

	Libor libor();

	static LiborCurve of(ForwardCurve curve, Libor libor) {
		return new LiborCurve() {
			@Override
			public Libor libor() {
				return libor;
			}

			@Override
			public ForwardRate forwardRate(DateInterval period, DayCount dayCount) {
				return curve.forwardRate(period, dayCount);
			}
		};
	}
}
