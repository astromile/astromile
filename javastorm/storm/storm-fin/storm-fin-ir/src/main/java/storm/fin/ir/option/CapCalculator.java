package storm.fin.ir.option;

import storm.fin.com.*;

import java.util.function.*;

public interface CapCalculator {

	interface Result {
		double price(Side side);
	}

	Result calculate(CapFloorInfo cap);

	void subscribe(CapFloorInfo cap, Consumer<Result> consumer);
}
