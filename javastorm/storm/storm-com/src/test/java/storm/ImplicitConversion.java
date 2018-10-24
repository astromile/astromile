package storm;

import org.junit.*;
import storm.AlternativePerformanceTest.*;

/**
 * Demonstrates that implicit conversion from int to double does not harm performance (thanks to compiler perhaps)
 */
public class ImplicitConversion {
	private static final int XAsInt = 42;
	private static final double XAsDouble = XAsInt;

	//	@Ignore("Long performance test. Static proof.")
	@Test
	public void performance() {
		int n = 100_000_000;
		AlternativePerformanceTest.Result result = new AlternativePerformanceTest()
				.addAlternative(Alternative.of("Without conversion", this::woConversion))
				.addAlternative(Alternative.of("With conversion", this::withConversion))
				.test(n);
		result.report();
		result.assertSame(0.05);
	}

	private double woConversion() {
		return XAsDouble;
	}

	private double withConversion() {
		return XAsInt;
	}
}
