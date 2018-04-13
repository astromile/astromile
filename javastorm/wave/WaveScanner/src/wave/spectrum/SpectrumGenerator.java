package wave.spectrum;

import wave.data.Channel;
import wave.data.WaveData;
import wave.data.WaveInfo;
import wave.note.Bitch;

import java.util.List;

public interface SpectrumGenerator {

	WaveSpectrum generate(TimeWindow window);

	static SpectrumGenerator raw(WaveData wav, Channel channel) {
		return RawSpectrumGenerator.of(wav, channel);
	}

	static SpectrumGenerator raw(WaveInfo waveInfo, WaveData.SingleWave wave) {
		return RawSpectrumGenerator.of(waveInfo, wave);
	}

	static SpectrumGenerator aggregated(
						WaveInfo waveInfo, WaveData.SingleWave wave, List<Bitch> bitches) {
		return AggregatedSpectrumGenerator.ofMaximum((RawSpectrumGenerator) raw(waveInfo, wave), bitches);
	}
}

