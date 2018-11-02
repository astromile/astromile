package storm.wave;

import org.primefaces.model.chart.*;
import storm.wave.data.*;
import storm.wave.file.*;
import storm.wave.note.*;
import storm.wave.spectrum.*;

import javax.annotation.*;
import javax.enterprise.context.*;
import javax.inject.*;
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.time.*;
import java.util.*;
import java.util.logging.*;
import java.util.stream.*;

@SessionScoped
@Named("waveRepo")
public class WaveFilEJB implements Serializable {
	private final static Logger LOG = Logger.getLogger(WaveFilEJB.class.getName());
	private final static String UPLOAD_FOLDER = "c:/tmp/wave/upload";
	private final static boolean MOCK_SECOND_CHANNEL = true;

	private WaveFileInfo selectedFile;

	private WaveData waveData;

	public LineChartModel getWaveChartModel() {
		return waveChartModel;
	}

	public LineChartModel getSpectrumChartModel() {
		return spectrumChartModel;
	}

	private LineChartModel waveChartModel;

	private LineChartModel spectrumChartModel;
	@PostConstruct
	public void init() {
		createChartModels();
	}

	private void createChartModels() {
		waveChartModel = initLinearModel();
		waveChartModel.setTitle("Original Wave");
		waveChartModel.setLegendPosition("e");
		Axis yAxis = waveChartModel.getAxis(AxisType.Y);
		yAxis.setMin(0);
		yAxis.setMax(1);

		spectrumChartModel = initLinearModel();
		spectrumChartModel.setTitle("Wave Spectrum");
		spectrumChartModel.setLegendPosition("e");
		yAxis = spectrumChartModel.getAxis(AxisType.Y);
		yAxis.setMin(0);
		yAxis.setMax(10);
	}

	private LineChartModel initLinearModel() {
		LineChartModel model = new LineChartModel();

		LineChartSeries series1 = new LineChartSeries();
		series1.setLabel("Left");

		series1.set(1, 2);
		series1.set(2, 1);
		series1.set(3, 3);
		series1.set(4, 6);
		series1.set(5, 8);

		LineChartSeries series2 = new LineChartSeries();
		series2.setLabel("Right");

		series2.set(1, 6);
		series2.set(2, 3);
		series2.set(3, 2);
		series2.set(4, 7);
		series2.set(5, 9);

		model.addSeries(series1);
		model.addSeries(series2);

		return model;
	}

	public List<WaveFileInfo> getFiles() {
		return loadFileInfos();
	}

	private List<WaveFileInfo> loadFileInfos() {
		try (Stream<Path> paths = Files.walk(Paths.get(UPLOAD_FOLDER))) {
			return paths
					.filter(Files::isRegularFile)
					.filter(path -> path.toString().endsWith(".upload"))
					.map(path -> {
						try {
							BasicFileAttributes attributes = Files.readAttributes(path, BasicFileAttributes.class);
							String originalFileName = path.getFileName().toString().split("-")[0];
							long size = attributes.size();
							LocalDateTime uploaded = LocalDateTime.ofInstant(attributes.creationTime().toInstant(),
									ZoneOffset.ofHours(2));
							return WaveFileInfo.of(originalFileName, path.getFileName(), size, uploaded);
						} catch (Exception e) {
							LOG.warning("Failed extracting information about " + path.getFileName() + ": " + e);
							return null;
						}
					}).filter(Objects::nonNull).collect(Collectors.toList());
		} catch (IOException e) {
			LOG.severe("Failed loading files from upload directory " + e);
			return Collections.emptyList();
		}
	}

	public WaveData getWaveData() {
		return waveData;
	}

	public WaveFileInfo getSelectedFile() {
		return selectedFile;
	}

	public void setSelectedFile(WaveFileInfo selectedFile) {
		if (selectedFile == null) {return;}
		this.selectedFile = selectedFile;
		try {
			File file = Paths.get(UPLOAD_FOLDER).resolve(selectedFile.getPath()).toFile();
			WavFile wavFile = WavFile.openWavFile(file);
			waveData = WaveFileData.of(wavFile);
			updateCharts();
		} catch (Exception e) {
			LOG.severe("Failed loading file " + selectedFile.getName());
		}
	}

	private void updateCharts() {
		waveChartModel.getSeries().clear();
		int nbOfChannels = waveData.getInfo().getNbOfChannels();
		IntStream.range(0, nbOfChannels).mapToObj(i -> Channel.of(i, nbOfChannels)).map(this::waveSeries)
				.forEach(waveChartModel.getSeries()::add);
		if (nbOfChannels == 1 && MOCK_SECOND_CHANNEL) {
			waveChartModel.getSeries().add(waveSeries(Channels.Mono));
			waveChartModel.getSeries().get(0).setLabel(Channels.Left.getName());
			waveChartModel.getSeries().get(1).setLabel(Channels.Right.getName());
		}

		spectrumChartModel.getSeries().clear();
		IntStream.range(0, nbOfChannels).mapToObj(i -> Channel.of(i, nbOfChannels)).map(this::spectrumSeries)
				.forEach(spectrumChartModel.getSeries()::add);
	}

	private LineChartSeries spectrumSeries(Channel channel) {
		LineChartSeries series = new LineChartSeries(channel.getName());
		SpectrumGenerator generator = SpectrumGenerator
				.aggregated(waveData.getInfo(), waveData.getWave(channel), Octaves.SecondOctave.getBitches());
		WaveSpectrum spectrum = generator.generate(TimeWindow.of(0, waveData.getInfo().getDuration()));
		spectrum.points().stream().forEach(p -> series.set(p.frequency(), p.amplitude()));
		return series;
	}

	private LineChartSeries waveSeries(Channel channel) {
		LineChartSeries series = new LineChartSeries(channel.getName());
		series.setShowMarker(false);
		double[] wave = waveData.getWave(channel).wave();
		int nbOfPoints = 100;
		int sampleStep = wave.length / nbOfPoints;
		double[] x = new double[nbOfPoints];
		double[] y = new double[nbOfPoints];
		for (int i = 0; i < nbOfPoints; ++i) {
			x[i] = (0.5 + i) * sampleStep / waveData.getInfo().getFrameRate();
			y[i] = IntStream.range(i * sampleStep, (i + 1) * sampleStep).mapToDouble(j -> Math.abs(wave[j]))
					.average().getAsDouble();
		}
		double maxAmplitude = DoubleStream.of(y).max().getAsDouble();
		IntStream.range(0, nbOfPoints).forEach(i -> series.set(x[i], y[i] / maxAmplitude));
		return series;
	}

	public void resetSelectedFile() {
		selectedFile = null;
	}
}
