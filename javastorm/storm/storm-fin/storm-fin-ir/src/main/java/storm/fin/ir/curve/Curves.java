package storm.fin.ir.curve;

import storm.fin.ir.*;

import java.time.*;
import java.util.*;
import java.util.stream.*;

public interface Curves {
	LocalDate baseDate();

	DiscountCurve discountCurve();

	Optional<ForwardCurve> forwardCurve(Libor libor);

	static Curves of(LocalDate baseDate,
	                 DiscountCurve discountCurve, Map<Libor, ForwardCurve> forwardCurveMap) {
		return new Curves() {
			@Override
			public LocalDate baseDate() {
				return baseDate;
			}

			@Override
			public DiscountCurve discountCurve() {
				return discountCurve;
			}

			@Override
			public Optional<ForwardCurve> forwardCurve(Libor libor) {
				return Optional.ofNullable(forwardCurveMap.get(libor));
			}
		};
	}

	static Curves of(LocalDate baseDate, ZeroCurve discountCurve, Map<Libor, ZeroCurve> fwdCurveMap) {
		return of(baseDate, DiscountCurve.of(discountCurve, baseDate),
				fwdCurveMap.entrySet().stream().collect(Collectors.toMap(e -> e.getKey(),
						e -> ForwardCurve.of(DiscountCurve.of(e.getValue(), baseDate)))));
	}
}
