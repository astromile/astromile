package storm;

import org.junit.*;
import storm.AlternativePerformanceTest.*;

import java.util.function.*;

public class MethodOrIf {

	@Ignore("Long performance test. Static proof.")
	@Test
	public void performance() {
		int n = 100_000_000;
		double[] x = new double[30];
		AlternativePerformanceTest.Result result = new AlternativePerformanceTest()
				.addAlternative(Alternative.of("If-version",
						() -> EndPoint.Left.getViaIf(x) + EndPoint.Right.getViaIf(x)))
				.addAlternative(Alternative.of("Method-version",
						() -> EndPoint.Left.getViaIf(x)))
				.test(n);
		result.report();
		result.assertSame(0.05);
	}

	enum EndPoint {
		Left(x -> 0), Right(x -> x.length - 1);

		private final Function<double[], Integer> index;

		EndPoint(Function<double[], Integer> i) {index = i;}

		double getViaIf(double[] x) {
			return x[this == Left ? 0 : x.length - 1];
		}

		double getViaLambda(double[] x) {
			return x[index.apply(x)];
		}
	}

}
