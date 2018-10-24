package storm.fin.time;

public class TimeCounter {
	private long start;

	private TimeCounter() {
		start = System.nanoTime();
	}

	public static TimeCounter start() {
		return new TimeCounter();
	}

	public double count() {
		return count(System.nanoTime());
	}

	private double count(long end) {
		return 1e-9 * (end - start);
	}

	public double reset() {
		double count = count();
		start = System.nanoTime();
		return count;
	}
}
