package storm.fin.time;

import org.junit.*;

import static org.junit.Assert.*;

public class TimeCounterTest {

	@Test
	public void start() {
		TimeCounter counter = TimeCounter.start();
		lengthyJob();
		double firstMark = counter.count();
		smallJob();
		double secondMark = counter.count();
		assertTrue(firstMark < secondMark);
		double thirdMark = counter.reset();
		assertTrue(secondMark < thirdMark);
		double fourthMark = counter.reset();
		assertTrue(fourthMark < firstMark);
	}

	private static void lengthyJob() {
		String s = "abbbbb cccca";
		int sz = 1000000;
		while (sz-- > 0) {
			if (s.contains("a")) {
				s = s.replace("a", "A");
			} else {
				s = s.replace("A", "a");
			}
		}
	}

	private static void smallJob() {
	}

}