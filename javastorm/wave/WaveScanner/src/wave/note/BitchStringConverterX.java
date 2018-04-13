package wave.note;

import javafx.util.StringConverter;

public class BitchStringConverterX extends StringConverter<Bitch> implements BitchStringConverter {

	@Override
	public String toString(Bitch bitch) {
		return to(bitch);
	}

	@Override
	public Bitch fromString(String string) {
		return from(string);
	}

}
