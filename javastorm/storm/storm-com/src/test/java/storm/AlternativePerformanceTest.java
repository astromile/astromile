package storm;

import java.util.*;
import java.util.function.*;
import java.util.stream.*;

import static org.junit.Assert.*;

class AlternativePerformanceTest {
	interface Result {
		List<AlternativeResult> alternativeResults();

		default AlternativeResult getResult(Alternative a) {
			return alternativeResults().stream().filter(ar -> ar.alternative() == a).findAny()
					.orElse(null);
		}

		default AlternativeResult getResult(String a) {
			return alternativeResults().stream().filter(ar -> ar.alternative().name().equals(a)).findAny()
					.orElse(null);
		}

		static Result of(List<AlternativeResult> results) {
			return () -> results;
		}

		default AlternativeResult theBest() {
			return alternativeResults().stream()
					.min(Comparator.comparing(AlternativeResult::performance))
					.orElse(null);
		}

		default AlternativeResult theWorst() {
			return alternativeResults().stream()
					.max(Comparator.comparing(AlternativeResult::performance))
					.orElse(null);
		}

		default void assertBest(Alternative a, double tolerance) {
			assertBest(getResult(a), tolerance);
		}

		default void assertBest(String a, double tolerance) {
			assertBest(getResult(a), tolerance);
		}

		default void assertBest(AlternativeResult bestResult, double tolerance) {
			double bestPerformance = bestResult.performance() * (1.0 - tolerance);
			Optional<AlternativeResult> evenBetter = alternativeResults().stream()
					.filter(ar -> ar.performance() < bestPerformance)
					.findAny();
			assertFalse("There are better alternatives than " + bestResult.alternative().name()
			            + ", e.g. " + evenBetter.orElse(null),
					evenBetter.isPresent());
		}

		default void assertSame(double tolerance) {
			AlternativeResult best = theBest();
			double worstPerformance = best.performance() * (1.0 + tolerance);
			Optional<AlternativeResult> significantlyDifferent = alternativeResults().stream()
					.filter(ar -> ar.performance() > worstPerformance)
					.findAny();
			assertFalse(best + " is significantly better than "
			            + significantlyDifferent.orElse(null),
					significantlyDifferent.isPresent());
		}

		default void report() {
			alternativeResults().stream()
					.sorted(Comparator.comparing(AlternativeResult::performance))
					.forEach(System.out::println);
		}

		interface AlternativeResult {


			Alternative alternative();

			int nbOfExecutions();

			/**
			 * @return total time (in seconds) ellapsed by executing alternative
			 * {@link #nbOfExecutions()} times.
			 */
			double performance();

			/**
			 * @return average execution time (see {@link #performance()}) of alternative
			 */
			default double performancePerExecution() {return performance() / nbOfExecutions();}

			static AlternativeResult of(Alternative a, int nbOfExecutions, double performance) {
				return new AlternativeResult() {

					@Override
					public Alternative alternative() {
						return a;
					}

					@Override
					public int nbOfExecutions() {
						return nbOfExecutions;
					}

					@Override
					public double performance() {
						return performance;
					}

					@Override
					public String toString() {
						return String.format(Locale.UK, "%s elapsed %1.3f s (avg = %.0f ns/run)",
								a.name(), performance(), 1e9 * performancePerExecution());
					}
				};
			}

		}
	}

	interface Alternative {
		String name();

		void run();

		static <T> Alternative of(String name, Supplier<T> r) {
			return of(name, () -> {r.get();});
		}

		static Alternative of(String name, Runnable r) {
			return new Alternative() {
				@Override
				public String name() {
					return name;
				}

				@Override
				public void run() {
					r.run();
				}
			};
		}
	}

	private final List<Alternative> alternatives = new ArrayList<>();

	AlternativePerformanceTest addAlternative(Alternative a) {
		alternatives.add(a);
		return this;
	}

	Result test(int nbOfExecutions) {
		long[] ellapsed = new long[alternatives.size()];
		for (int i = nbOfExecutions; i-- > 0; ) {
			for (int a = 0; a < alternatives.size(); ++a) {
				ellapsed[a] -= System.nanoTime();
				alternatives.get(a).run();
				ellapsed[a] += System.nanoTime();
			}
		}
		return Result.of(IntStream.range(0, alternatives.size())
				.mapToObj(i -> Result.AlternativeResult
						.of(alternatives.get(i), nbOfExecutions, 1e-9 * ellapsed[i]))
				.collect(Collectors.toList()));
	}
}
