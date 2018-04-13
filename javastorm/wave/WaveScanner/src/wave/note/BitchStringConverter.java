package wave.note;

import kern.type.TwoWayConverter;

public interface BitchStringConverter extends TwoWayConverter<Bitch, String> {
	default String to(Bitch bitch) {
		if (bitch instanceof EquitemporedBitch) {
			EquitemporedBitch etBitch = (EquitemporedBitch) bitch;
			return etBitch.scientificNotation();
		}
		return bitch.frequency()+"Hz";
	}
	default Bitch from(String bitch) {
		return EquitemporedBitch.fromString(bitch);
	}
}
