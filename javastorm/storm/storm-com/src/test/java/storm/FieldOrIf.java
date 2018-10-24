package storm;

import org.junit.*;
import storm.AlternativePerformanceTest.*;

/**
 * Demonstrates that a field-version performs faster than if-else-switch-version, which is true if
 * there are more than two cases, otherwise performance is comparable and switch-version may be
 * more concise (namely by avoiding field declaration and corresponding getter-method definition)
 */
public class FieldOrIf {

	@Ignore("Long performance test. Static proof.")
	@Test
	public void comparePerformanceViaTester() {
		int n = 100_000_000;
		Result result = new AlternativePerformanceTest()
				.addAlternative(Alternative.of("If-version", () ->
						If.A1.index() + If.A2.index() + If.A3.index() + If.A4.index() + If.A5.index()))
				.addAlternative(Alternative.of("Field-version", () ->
						Field.A1.index() + Field.A2.index() + Field.A3.index() + Field.A4.index() + Field.A5.index()))
				.test(n);
		result.report();
		result.assertBest("Field-version", 0);
	}

	enum Field {
		A1(1), A2(2), A3(3), A4(4), A5(5);

		private final int index;

		Field(int i) {
			index = i;
		}

		int index() {
			return index;
		}

	}

	enum If {
		A1, A2, A3, A4, A5;

		int index() {
			switch (this) {
				case A1:
					return 1;
				case A2:
					return 2;
				case A3:
					return 3;
				case A4:
					return 4;
				case A5:
					return 5;
				default:
					throw new IllegalArgumentException("Unsupported " + getClass() + " value " + this);
			}
		}

	}

}

