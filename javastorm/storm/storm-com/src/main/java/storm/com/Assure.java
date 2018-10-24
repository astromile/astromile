package storm.com;

import java.util.*;
import java.util.function.*;

public interface Assure {

	static void that(boolean condition, Supplier<String> error) {
		if (!condition) {
			throw new IllegalStateException(error.get());
		}
	}

	static <T> T notNull(T t, Supplier<String> error) {
		return Objects.requireNonNull(t);
	}

	static <T> void notEmpty(Collection<T> t, Supplier<String> error) {
		that(!notNull(t, error).isEmpty(), error);
	}

	static <T, U> void sameSize(Collection<T> t, Collection<U> u, Supplier<String> error) {
		that(t.size() == u.size(),
				() -> "Incompatible sizes of lists (" + error.get() + "): " + t.size() + " vs. " + u.size());
	}

	static void sameSize(double[] t, double[] u, Supplier<String> error) {
		that(t.length == u.length, error);
	}

}
