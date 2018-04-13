package wave.spectrum.aggregate;

import org.junit.Test;
import wave.note.Bitch;
import wave.note.Octaves;
import wave.spectrum.SpectrumPoint;

import java.util.List;
import java.util.logging.Logger;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class SimpleIntervalGeneratorTest {
	private final static Logger LOGGER = Logger.getLogger(SimpleIntervalGeneratorTest.class.getName());

	@Test
	public void testIntervalGeneration(){
		List<Bitch> bitches = Octaves.SecondOctave.getBitches();
		SimpleIntervalGenerator generator = SimpleIntervalGenerator.of(bitches);
		List<SpectrumPoint> spectrum = IntStream.range(0,100)
							.mapToDouble(i->bitches.get(0).frequency()*0.9
												+ (1.1*bitches.get(bitches.size()-1).frequency()
												- 0.9*bitches.get(0).frequency())*i/100.)
							.mapToObj(frequency -> SpectrumPoint.of(frequency,0.0))
							.collect(Collectors.toList());
		List<Interval> intervals = generator.generate(spectrum);
		intervals.stream().map(i->String.format("%s(%s,%s)",i.pitch().frequency(),i.start(),i.end()))
							.forEach(LOGGER::info);
	}

}
