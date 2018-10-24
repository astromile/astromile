package storm.fin.ir.curve;

import storm.fin.ir.*;

import java.time.*;

public interface ZeroCurve {
	ZeroRate zeroRate(LocalDate date);
}
