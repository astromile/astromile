package storm.type;

/**
 * Generic <b>two-way</b> converter interface
 *
 * @param <S> source type
 * @param <T> target type
 */
public interface TwoWayConverter<S, T> {
	T to(S source);

	S from(T target);
}
