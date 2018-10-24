package storm.fin.time.schedule;

import java.time.*;
import java.util.*;

public interface Schedule {

	List<LocalDate> dates();

	default int size() {
		return dates().size();
	}

	static Schedule of(List<LocalDate> dates) {
		return () -> dates;
	}

}

