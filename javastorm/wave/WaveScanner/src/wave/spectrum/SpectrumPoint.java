package wave.spectrum;

import java.util.Comparator;

public interface SpectrumPoint {
	double frequency();
	double amplitude();

	static SpectrumPoint of(double frequency, double amplitude){
		return new SpectrumPoint() {
			@Override
			public double frequency() {
				return frequency;
			}

			@Override
			public double amplitude() {
				return amplitude;
			}
		};
	}

	static Comparator<SpectrumPoint> compareByAmplitude(){
		return (p1,p2)->{
			return (int) Math.signum(p1.amplitude()-p2.amplitude());
		};
	}

	static Comparator<SpectrumPoint> compareByAmplitudeAndFrequency(){
		return (p1,p2)->{
			int c= (int) Math.signum(p1.amplitude()-p2.amplitude());
			if(c==0){
				return (int)Math.signum((p1.frequency()-p2.frequency()));
			}else{
				return c;
			}
		};
	}

	static Comparator<SpectrumPoint> compareByFrequency(){
		return (p1,p2)->{
			return (int) Math.signum(p1.frequency()-p2.frequency());
		};
	}
}
