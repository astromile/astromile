package storm.math.interpol;

import org.apache.commons.math3.random.*;
import org.junit.*;

import java.util.stream.*;

public class ResettableInterpolationFunctionTest {

	@Test
	public void testD1vsD2() {
		MersenneTwister mt = new MersenneTwister(201581001);
		int n = 1000_000;
		double[] x, dx;
		long start;
		long ellapsedD1 = 0, ellapsedD2 = 0;
		for (int i = 0; i < n; i++) {
			x = IntStream.range(0, 100).mapToDouble(j -> mt.nextDouble()).toArray();
			start = System.nanoTime();
			dx = ExtrapolationFunction.d2(x);
			ellapsedD2 += System.nanoTime() - start;
			start = System.nanoTime();
			dx = ExtrapolationFunction.d1(x);
			ellapsedD1 += System.nanoTime() - start;
		}
		System.out.println("Ellapsed D1: " + ellapsedD1 / n + " ns/dx");
		System.out.println("Ellapsed D2: " + ellapsedD2 / n + " ns/dx");
	}

}