package wave.spectrum.aggregate;

import wave.note.Bitch;
import wave.spectrum.AggregatedSpectrumGenerator;

import java.util.List;

public interface PitchAggregator extends AggregatedSpectrumGenerator.Aggregator {

	List<Bitch> getBitches();

}
