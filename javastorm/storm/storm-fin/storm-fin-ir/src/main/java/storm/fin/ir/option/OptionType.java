package storm.fin.ir.option;

public enum OptionType {
	Call(1), Put(-1);

	private final double phi;

	OptionType(int phi) {this.phi = phi;}

	public double getPayOffFactor() {
		return phi;
	}
}
