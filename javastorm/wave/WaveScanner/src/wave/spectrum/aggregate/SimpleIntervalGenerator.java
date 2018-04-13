package wave.spectrum.aggregate;

import wave.note.Bitch;
import wave.note.EquitemporedBitch;
import wave.spectrum.SpectrumPoint;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class SimpleIntervalGenerator implements Interval.Generator {
	private final List<Bitch> bitches;
	private final List<DoubleInterval> intervals;

	private interface DoubleInterval {
		double start();

		double end();

		static DoubleInterval of(double start, double end) {
			return new DoubleInterval() {
				@Override
				public double start() {
					return start;
				}

				@Override
				public double end() {
					return end;
				}
			};
		}
	}

	private SimpleIntervalGenerator(List<Bitch> bitches) {
		this.bitches = bitches;
		this.bitches.sort(Comparator.comparing(Bitch::frequency));
		this.intervals = generateIntervals(bitches);
	}

	public static SimpleIntervalGenerator of(List<Bitch> bitches){
		return new SimpleIntervalGenerator(bitches);
	}

	private List<DoubleInterval> generateIntervals(List<Bitch> bitches) {
		double quarterTone = Math.sqrt(EquitemporedBitch.HALFTONE_FACTOR);
		List<DoubleInterval> intervals = bitches.stream()
							.map(bitch -> DoubleInterval.of(
												bitch.frequency() / quarterTone, bitch.frequency() * quarterTone))
							.collect(Collectors.toList());
		return ensureNonOverlapping(intervals);
	}

	private List<DoubleInterval> ensureNonOverlapping(List<DoubleInterval> intervals) {
		IntStream.range(0, intervals.size() - 1)
							.filter(i -> intervals.get(i).end() > intervals.get(i + 1).start())
							.forEach(i -> {
								double mid = 0.5 * (intervals.get(i).end() + intervals.get(i + 1).start());
								intervals.set(i, DoubleInterval.of(intervals.get(i).start(), mid));
								intervals.set(i + 1, DoubleInterval.of(mid, intervals.get(i + 1).end()));
							});
		return intervals;
	}

	@Override
	public List<Interval> generate(List<SpectrumPoint> points) {
		List<Interval> pIntervals = new ArrayList<>(bitches.size());
		int start = IntStream.range(0, points.size())
							.filter(i -> points.get(i).frequency() >= intervals.get(0).start())
							.findFirst().orElse(points.size());
		int end = start;
		int interval = 0;
		while (end < points.size()) {
			if (points.get(end).frequency() > intervals.get(interval).end()) {
				pIntervals.add(Interval.of(bitches.get(interval), start, end));
				start = end;
				interval += 1;
				if(interval==intervals.size()){
					break;
				}
			} else {
				end += 1;
			}
		}
		return pIntervals;
	}
}
