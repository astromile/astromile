package storm.fin.com;

import org.junit.*;

import java.util.*;

import static org.junit.Assert.*;

public class CcyTest {

	@Test
	public void EUR_IsPresent() {
		assertEquals(Ccy.EUR, Currency.getInstance("EUR"));
		assertTrue(Ccy.EUR == Currency.getInstance("EUR"));
	}

}