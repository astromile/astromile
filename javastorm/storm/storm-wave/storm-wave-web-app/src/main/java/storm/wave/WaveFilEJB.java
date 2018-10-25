package storm.wave;

import org.primefaces.model.chart.*;

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

	private WaveFileInfo selectedFile;

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
		yAxis.setMax(10);

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
		try (Stream<Path> paths = Files.walk(Paths.get("c:/tmp/wave/upload"))) {
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
							return WaveFileInfo.of(originalFileName, size, uploaded);
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

	public WaveFileInfo getSelectedFile() {
		return selectedFile;
	}

	public void setSelectedFile(WaveFileInfo selectedFile) {
		this.selectedFile = selectedFile;
	}

	public void resetSelectedFile() {
		selectedFile = null;
	}
}
