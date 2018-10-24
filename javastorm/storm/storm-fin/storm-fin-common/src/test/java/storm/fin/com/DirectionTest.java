package storm.fin.com;

import org.junit.*;

import static org.junit.Assert.*;

public class DirectionTest {

	@Test
	public void of() {
		assertEquals(Direction.Forward, Direction.of(1));
		assertEquals(Direction.Forward, Direction.of(42));
		assertEquals(Direction.Backward, Direction.of(-876542132));
		assertEquals(Direction.Undefined, Direction.of(0));
	}

	@Test
	public void getValue() {
		assertEquals(1, Direction.Forward.getValue());
		assertEquals(0, Direction.Undefined.getValue());
		assertEquals(-1, Direction.Backward.getValue());
	}

	@Test
	public void opposite() {
		assertEquals(Direction.Backward, Direction.Forward.opposite());
		assertEquals(Direction.Forward, Direction.Backward.opposite());
		assertEquals(Direction.Undefined, Direction.Undefined.opposite());
	}
}