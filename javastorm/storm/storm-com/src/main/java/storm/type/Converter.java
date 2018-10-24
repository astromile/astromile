package storm.type;

/**
 * Generic <b>one-way</b> converter interface
 *
 * @param <S> source type
 * @param <T> target type
 */
public interface Converter<S, T> {
	T convert(S source);
}
