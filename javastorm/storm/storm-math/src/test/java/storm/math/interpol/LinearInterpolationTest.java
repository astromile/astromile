package storm.math.interpol;

import org.junit.*;
import storm.math.interpol.LinearInterpolation.*;
import storm.math.interpol.LinearInterpolation.PiecewiseLinearFunction.*;

import java.util.stream.*;

import static org.junit.Assert.*;

public class LinearInterpolationTest {

	@Test
	public void interpolation() {
		double[] y = {0, 1, 0, 2};
		double[] x = {0, 1, 2, 3};
		Interpolation.Function f = Interpolation.linear(ExtrapolationMethod.of(null, null))
				.interpolate(x, y);
		/* all points match exactly */
		IntStream.range(0, x.length).forEach(i -> assertEquals(y[i], f.at(x[i]).get(), 0));
		double doublePrecision = 1e-16;
		assertEquals(0.1, f.at(0.1).get(), doublePrecision);
		assertEquals(0.1, f.at(1.9).get(), doublePrecision);
		assertEquals(1.0, f.at(2.5).get(), doublePrecision);
	}

	@Test
	public void exrapolationConst() {
		double[] y = {0, 1, 0, 2};
		double[] x = {0, 1, 2, 3};
		Interpolation.Function f = Interpolation.linear(
				ExtrapolationMethod.of(Extrapolation.Constant, Extrapolation.Constant))
				.interpolate(x, y);
		double doublePrecision = 1e-16;
		assertEquals(y[0], f.at(x[0]).get(), 0);
		assertEquals(y[0], f.at(x[0] - 1).get(), 0);
		assertEquals(y[y.length - 1], f.at(x[x.length - 1]).get(), 0);
		assertEquals(y[y.length - 1], f.at(x[x.length - 1] + 1).get(), 0);
	}

	@Test
	public void exrapolationLinear() {
		double[] y = {0, 1, 0, 2};
		double[] x = {0, 1, 2, 3};
		Interpolation.Function f = Interpolation.linear(
				ExtrapolationMethod.of(Extrapolation.Linear, Extrapolation.Linear))
				.interpolate(x, y);
		double doublePrecision = 1e-16;
		assertEquals(y[0], f.at(x[0]).get(), 0);
		assertEquals(-1, f.at(-1).get(), doublePrecision);
		assertEquals(y[y.length - 1], f.at(x[x.length - 1]).get(), 0);
		assertEquals(4, f.at(4).get(), doublePrecision);
	}

	@Test(expected = NullPointerException.class)
	public void failTo_InterpolateNullX() {
		LinearInterpolation li = Interpolation.linear(ExtrapolationMethod.of(null, null));
		li.interpolate(null, new double[0]);
	}

	@Test(expected = IllegalStateException.class)
	public void failTo_InterpolateEmptyX() {
		LinearInterpolation li = Interpolation.linear(ExtrapolationMethod.of(null, null));
		li.interpolate(new double[0], new double[0]);
	}

	@Test(expected = IllegalStateException.class)
	public void failTo_InterpolateIncompatibleXY() {
		LinearInterpolation li = Interpolation.linear(ExtrapolationMethod.of(null, null));
		li.interpolate(new double[1], new double[2]);
	}

	@Test(expected = IllegalStateException.class)
	public void failTo_ExtrapolateLinearSinglePoint() {
		LinearInterpolation li = Interpolation.linear(ExtrapolationMethod.of(Extrapolation.Linear, null));
		li.interpolate(new double[1], new double[1]);
	}

}