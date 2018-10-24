package storm.fin.ir.swap;

import storm.com.*;
import storm.fin.ir.*;

import java.time.*;

public interface RateMarket {
	DoubleValue rate(LocalDate fixingDate, Libor libor);
}
