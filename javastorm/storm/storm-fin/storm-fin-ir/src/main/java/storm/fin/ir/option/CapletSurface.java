package storm.fin.ir.option;

import storm.fin.ir.*;

import java.time.*;

public interface CapletSurface {
	Model model(LocalDate expiry, Libor index);
}
