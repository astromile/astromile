package storm.fin.com;

import org.junit.*;

import static org.junit.Assert.*;

public class SideTest {

	@Test
	public void getValue() {
		assertEquals(1, Side.Buy.getValue());
		assertEquals(0, Side.Mid.getValue());
		assertEquals(-1, Side.Sell.getValue());
	}

}