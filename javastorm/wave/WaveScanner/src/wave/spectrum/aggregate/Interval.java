package wave.spectrum.aggregate;

import wave.note.Bitch;
import wave.spectrum.SpectrumPoint;

import java.util.List;

public interface Interval {
	int start();
	int end();
	Bitch pitch();
	default List<SpectrumPoint> points(List<SpectrumPoint> points){
		return points.subList(start(),end());
	}
	static Interval of(Bitch bitch, int start, int end){
		return new Interval() {
			@Override
			public int start() {
				return start;
			}

			@Override
			public int end() {
				return end;
			}

			@Override
			public Bitch pitch() {
				return bitch;
			}
		};
	}

	interface Generator {
		List<Interval> generate(List<SpectrumPoint> points);
	}
}
