package storm.fin.ir.option;

public interface Model {
	double undiscountedPrice(double strike, OptionType type);
}
