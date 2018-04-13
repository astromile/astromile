package wave.view;

import com.sun.javafx.charts.*;
import com.sun.javafx.collections.*;
import javafx.animation.*;
import javafx.application.*;
import javafx.collections.*;
import javafx.concurrent.*;
import javafx.event.*;
import javafx.fxml.*;
import javafx.scene.chart.*;
import javafx.scene.control.Button;
import javafx.scene.control.*;
import javafx.scene.control.Label;
import javafx.scene.input.*;
import javafx.stage.*;
import javafx.stage.Window;
import javafx.util.Duration;
import javafx.util.*;
import wave.data.*;
import wave.file.*;
import wave.note.*;
import wave.play.*;
import wave.spectrum.*;

import java.awt.*;
import java.io.*;
import java.time.*;
import java.util.*;
import java.util.List;
import java.util.concurrent.atomic.*;
import java.util.function.*;
import java.util.logging.*;
import java.util.stream.*;

public class WaveViewController {
	enum SpectrumType {
		Raw, Aggregated
	}

	enum SpectrumViewType {
		Static, Dynamic
	}

	final static Logger LOG
					= Logger.getLogger(WaveViewController.class.getName());
	private final static int scale = 1024;
	private static final StringConverter<Number> bitchConverter = new StringConverter<Number>() {
		@Override
		public String toString(Number frequency) {
			EquitemporedBitch bitch = EquitemporedBitch.Factory.INSTANCE.forStep(
							(int) Math.round(frequency.doubleValue()));
			return Optional.ofNullable(Bitches.of(bitch)).map(Bitches::toString)
							       .orElse("440Hz " + (frequency.intValue() >= 0 ? " +" : "") + frequency.intValue());
		}

		@Override
		public Number fromString(String string) {
			return Bitches.valueOf(string).step();
		}
	};
	private static final StringConverter<Number> doubleConverter = new StringConverter<Number>() {
		@Override
		public String toString(Number object) {
			return object.toString();
		}

		@Override
		public Number fromString(String string) {
			return Double.valueOf(string);
		}
	};
	final ChartCoordinates waveCoordinates = ChartCoordinates.of(this);
	private final FileChooser openFileDialog = new FileChooser();
	private final TimeWindowLimit timeBar = new TimeWindowLimit(this, 0.);
	public Label lblFileInfo;
	public Label lblStatus;
	public LineChart chartWave;
	public LineChart chartFreq;
	public NumberAxis xAxis;
	public NumberAxis yAxis;
	public NumberAxis xAxisFreq;
	public NumberAxis yAxisFreq;
	public ChoiceBox choiceOfChannel;
	public ComboBox comboSampling;
	public ChoiceBox choiceOfSpectrumType;
	public ChoiceBox choiceOfView;
	public Button btnPlay;
	WaveData waveData;
	AtomicBoolean isListenerSet = new AtomicBoolean(false);
	TimeWindowLimit limMin = new TimeWindowLimit(this, 0.);
	TimeWindowLimit limMax = new TimeWindowLimit(this, 1.);
	TimeWindowLimit selectedLimit = null;
	private Window stage;
	private File directory;
	private Desktop desktop = Desktop.getDesktop();

	public WaveViewController() {
		LOG.setLevel(Level.WARNING);
		openFileDialog.setTitle("Load WAV file");
		directory = new File("c:\\tmp");
	}

	public void playFile(ActionEvent actionEvent) {
		startMovingTimeBar();
		String fileName = null;
		try {
			fileName = ((WaveFileData) waveData).getFileName();
			WavPlayer.of(fileName).play();
		} catch (IOException e) {
			LOG.severe(e.getMessage());
			lblStatus.setText("Could not open file " + fileName);
		}
	}

	private void startMovingTimeBar() {
		double period = 0.1;
		double windowWidth = period;
		//timeBar.addToChart();
		timeBar.moveTo(0.);
		Timeline barMover = new Timeline(new KeyFrame(Duration.seconds(period), new EventHandler<ActionEvent>() {
			@Override
			public void handle(ActionEvent event) {
				timeBar.moveTo(timeBar.x + period);
				if (getSpectrumViewType() == SpectrumViewType.Static) {
					limMin.moveTo(timeBar.x);
					limMax.moveTo(timeBar.x + windowWidth);
					plotChannelsSpectrum();
				}
			}
		}));
		barMover.setCycleCount((int) Math.floor(waveData.getInfo().getDuration() / period));
		barMover.play();
	}

	private SpectrumViewType getSpectrumViewType() {
		return SpectrumViewType.valueOf(choiceOfView.getValue().toString());
	}

	private void plotChannelsSpectrum() {
		plotChannelsSpectrum(selectChannels(choiceOfChannel.getSelectionModel()
						                                    .getSelectedIndex()));
	}

	void plotChannelsSpectrum(List<Integer> channels) {
		chartFreq.getData().clear();
		channels.forEach(this::plotSpectrum);
		IntStream.range(0, channels.size()).forEach(i ->
						                                            setLineColor(chartFreq, i, getColor(channels.get(i))));
		/* remove redundant plots if necessary */
//		if (chartFreq.getData().size() > channels.size()) {
//			chartFreq.getData().remove(channels.size(), chartFreq.getData().size());
//		}
		/* remove spectrum legend as it is a duplicate of wave legend */
		((Legend) chartFreq.lookup(".chart-legend")).getItems().clear();

		tuneAxes();

	}

	List<Integer> selectChannels(int channel) {
		if (channel < waveData.getInfo().getNbOfChannels()) {
			return Collections.singletonList(channel);
		} else {
			return IntStream.range(0, waveData.getInfo().getNbOfChannels()).boxed().collect
							                                                                        (Collectors.toList());
		}
	}

	private void setLineColor(LineChart chart, int i, String color) {
		Optional.ofNullable(color).ifPresent(c -> {
			Platform.runLater(() -> {
				Optional.ofNullable(chart.lookup(
								".default-color" + i + ".chart-series-line"))
								.map(series -> {
									series.setStyle("-fx-stroke: #" + c + ";");
									return null;
								});
//								.orElseThrow(() -> new IllegalArgumentException(
//													"No chart series found"));
				Optional.ofNullable(chart.lookup("" +
				                                 ".default-color" + i +
				                                 ".chart-line-symbol"))
								.ifPresent(legend ->
												           legend.setStyle("-fx-background-color: #" + c + ";")
								);
			});
		});
	}

	private String getColor(int chIdx) {
		if (waveData.getInfo().getNbOfChannels() == 1) {
			return "0000ff";
		} else if (chIdx == 0) {
			return "ff0000";
		} else if (chIdx == 1) {
			return "00ff00";
		}
		return null;
	}

	private void tuneAxes() {
		if (getSpectrumViewType() == SpectrumViewType.Dynamic) {
			yAxisFreq.setAutoRanging(true);
			xAxisFreq.setAutoRanging(false);
			xAxisFreq.setLowerBound(0.0);
			xAxisFreq.setUpperBound(waveData.getInfo().getDuration());
			yAxisFreq.setTickLabelFormatter(bitchConverter);
		} else {
			xAxisFreq.setAutoRanging(true);
			yAxisFreq.setAutoRanging(false);
			yAxisFreq.setLowerBound(0.0);
			yAxisFreq.setUpperBound(1.0);
			yAxisFreq.setTickLabelFormatter(doubleConverter);
		}
		yAxisFreq.setTickLabelFormatter(getSpectrumViewType() == SpectrumViewType.Dynamic
		                                ? bitchConverter : doubleConverter);
	}

	public void viewChanged(ActionEvent actionEvent) {
		xAxisFreq.setTickLabelFormatter(getSpectrumViewType() == SpectrumViewType.Dynamic
		                                ? doubleConverter : bitchConverter);
		plotChannelsSpectrum();
	}

	public void samplingChanged(ActionEvent event) {
		plotSelectedChannels(choiceOfChannel.getSelectionModel().getSelectedIndex());
	}

	private void plotSelectedChannels(int channel) {
		List<Integer> channels = selectChannels(channel);
		/* waves itself */
		plotChannelsWaves(channels);
		/* spectrum */
		plotChannelsSpectrum(channels);
	}

	private void plotChannelsWaves(List<Integer> channels) {
		LOG.info("Clearing chartWave...");
		chartWave.getData().removeIf(series ->
						                             !((XYChart.Series) series).getName().equals("Limit"));
		channels.forEach(this::plotChannel);
		xAxis.setLowerBound(-0.01 * waveData.getInfo().getDuration());
		xAxis.setUpperBound(1.01 * waveData.getInfo().getDuration());
		Stream.of(limMin, limMax).forEach(lim -> lim.series.getNode().toFront());
		IntStream.range(0, channels.size()).forEach(i ->
						                                            setLineColor(chartWave, 2 + i, getColor(channels.get(i))));
		Legend legend = (Legend) chartWave.lookup(".chart-legend");
		legend.getItems().removeIf(item -> item.getText().equals("Limit"));
	}

	public void spectrumTypeChanged(ActionEvent actionEvent) {
		SpectrumType spectrumType = getSpectrumType();
		if (spectrumType == SpectrumType.Aggregated) {
			choiceOfView.setDisable(false);
		} else {
			choiceOfView.setDisable(true);
			choiceOfView.setValue(SpectrumViewType.Static.toString());
		}

		plotChannelsSpectrum();
	}

	private SpectrumType getSpectrumType() {
		return SpectrumType.valueOf(choiceOfSpectrumType.getValue().toString());
	}

	private void plotSpectrum(int chIdx) {
		Channel channel = Channel.of(chIdx, waveData.getInfo().getNbOfChannels());
		SpectrumGenerator spectrumGenerator = getSpectrumGenerator(channel);
		switch (getSpectrumViewType()) {
			case Static:
				List<XYChart.Data> data = getStaticData(spectrumGenerator);
				addSeries(chartFreq, channel.getName(), data);
				break;
			case Dynamic:
				List<List<XYChart.Data>> lines = getDynamicData(spectrumGenerator);
				IntStream.range(0, lines.size()).forEach(i ->
								                                         addSeries(chartFreq, channel.getName() + i, lines.get(i)));
				break;
			default:
				throw new IllegalArgumentException(
								"Unsupported Spectrum View Type '" + getSpectrumViewType() + "'");
		}
	}

	private SpectrumGenerator getSpectrumGenerator(Channel channel) {
		SpectrumGenerator generator;
		switch (getSpectrumType()) {
			case Raw:
				return SpectrumGenerator.raw(waveData, channel);
			case Aggregated:
				List<Bitch> bitches = Stream.concat(
								Octaves.SecondOctave.getBitches().stream(),
								Stream.of(Octaves.ThirdOctave.getBitches().get(0)))
								                      .collect(Collectors.toList());
				return SpectrumGenerator.aggregated(waveData.getInfo(), waveData.getWave(channel), bitches);
			default:
				throw new UnsupportedOperationException("Unknown frequency type " + choiceOfSpectrumType.getValue());
		}
	}

	private List<XYChart.Data> getStaticData(SpectrumGenerator generator) {
		long start = System.currentTimeMillis();
		WaveSpectrum spectrum = generator.generate(TimeWindow.of(limMin.x, limMax.x));
		long end = System.currentTimeMillis();
		lblStatus.setText("Static spectrum computed in " + (end - start) / 1000. + "s");

		List<SpectrumPoint> points = spectrum.points();
		if (getSpectrumType() == SpectrumType.Raw) {
			points = getTopAmplitudePoints(points, 100);
		}
		List<XYChart.Data> data = new ArrayList<>(3 * points.size());
		points.stream().forEach(p -> data.addAll(Stream.of(0., p.amplitude(), 0.)
						                                         .map(a -> new XYChart.Data(getHarmonicFreq(p.frequency()), a))
						                                         .collect(Collectors.toList())));
		return data;
	}

	private void addSeries(LineChart chart, String name, List<XYChart.Data> data) {
		Optional<XYChart.Series> series = chart.getData().stream()
						                                  .filter(s -> ((XYChart.Series) s).getName().equals(name))
						                                  .findAny();
		if (series.isPresent()) {
			series.get().setData(new ObservableListWrapper(data));
		} else {
			XYChart.Series newSeries = new XYChart.Series();
			newSeries.setName(name);
			newSeries.getData().addAll(data);
			chart.getData().add(newSeries);
		}
	}

	private List<List<XYChart.Data>> getDynamicData(SpectrumGenerator generator) {
		int windowSize = 4096;
		int nbOfPoints = 100;
		double windowWidth = 0.5 * (double) waveData.getInfo().getFrameRate() / windowSize;

		Map<Double, List<XYChart.Data>> lines = new HashMap<>();
		TimeWindow fullWindow = TimeWindow.of(limMin.x, limMax.x);
		double halfInterval = (double) windowSize / waveData.getInfo().getFrameRate();
		double dt = (limMax.x - limMin.x) / nbOfPoints;
		DoubleUnaryOperator scale = (a) -> windowWidth * a;
		IntStream.range(0, nbOfPoints).forEach(i -> {
			double t = limMin.x + i * dt;
			WaveSpectrum spectrum = generator.generate(TimeWindow.of(t - halfInterval, t + halfInterval));
			spectrum.points().forEach(point ->
							                          lines.computeIfAbsent(point.frequency(), f -> new ArrayList())
											                          .add(new XYChart.Data(t,
											                                                getHarmonicFreq(point.frequency())
											                                                + scale.applyAsDouble(point.amplitude()))));
		});
		return lines.values().stream().collect(Collectors.toList());
	}

	private List<SpectrumPoint> getTopAmplitudePoints(
					List<SpectrumPoint> points, int nFreqs) {
		Comparator<? super SpectrumPoint> amplitudeComparator
						= SpectrumPoint.compareByAmplitudeAndFrequency();
		SortedSet<SpectrumPoint> top = new TreeSet<>(amplitudeComparator);
		top.addAll(points.subList(0, nFreqs));
		SpectrumPoint min = top.first();
		for (int i = nFreqs; i < points.size(); ++i) {
			if (amplitudeComparator.compare(points.get(i), min) > 0) {
				top.add(points.get(i));
				top.remove(min);
				min = top.first();
			}
		}
		return top.stream().sorted(SpectrumPoint.compareByFrequency())
						       //.map(p -> SpectrumPoint.of(getHarmonicFreq(p.frequency()), p.amplitude()))
						       .collect(Collectors.toList());
	}

	private double getHarmonicFreq(double freq) {
		double a2 = 440.;
		return 12 * Math.log(freq / a2) / Math.log(2);
	}

	@FXML
	protected void initialize() {
		lblStatus.setText("Choose file");
	}

	@FXML
	private void openFile(ActionEvent actionEvent) {
		configureDialog();
		File wavFile = openFileDialog.showOpenDialog(stage);
		if (wavFile != null) {
			loadFile(wavFile);
		} else {
			lblFileInfo.setText("No file selected...");
		}
	}

	private void configureDialog() {
		openFileDialog.setInitialDirectory(directory);
		openFileDialog.setInitialFileName("cdur_sin.wav");
	}

	private void loadFile(File wavFile) {
		Task<Void> loadTask = new Task<Void>() {
			@Override
			protected Void call() throws Exception {
				try {
					Platform.runLater(() -> lblStatus.setText("Loading " + wavFile
									                                                       .getName() + "..."));
					long start = System.currentTimeMillis();
					WaveData tmpData = WaveData.of(WavFile.openWavFile(wavFile));
					WaveInfo info = tmpData.getInfo();
					info = WaveInfo.of(2, info.getNbOfFrames(), info.getFrameRate());
					waveData = new WaveFileData(wavFile.getPath(), info, Arrays.asList(
									tmpData.getWave(Channels.Mono), tmpData.getWave(Channels.Mono)));
					long end = System.currentTimeMillis();
					Platform.runLater(() ->
					                  {
						                  showFileInfo(wavFile.getName(), end - start);
						                  updateControls();
						                  lblStatus.setText("File " + wavFile.getName() + " loaded");
					                  });
					//plotSelectedChannels(0);
				} catch (IOException e) {
					Platform.runLater(() -> showError(e));
				} catch (WavFileException e) {
					Platform.runLater(() -> showError(e));
				}
				return null;
			}
		};
		new Thread(loadTask).start();
	}

	private void showFileInfo(String name, long elapsedMillis) {
		StringBuilder info = new StringBuilder();
		info.append(name).append(" loaded @").append(LocalTime.now())
						.append(" in ").append(elapsedMillis / 1000.).append(" s\n")
						.append("Nb of channels     : ").append(waveData.getInfo().getNbOfChannels()).append("\n")
						.append("Total nb of frames : ").append(waveData.getInfo().getNbOfFrames()).append("\n")
						.append("Frame rate (fps)   : ").append(waveData.getInfo().getFrameRate()).append("\n")
						.append("Duration     (s)   : ").append(waveData.getInfo().getDuration()).append("\n");
		lblFileInfo.setText(info.toString());
	}

	private void updateControls() {
		choiceOfChannel.setDisable(waveData.getInfo().getNbOfChannels() == 1);
		choiceOfView.setDisable(getSpectrumType() != SpectrumType.Aggregated);
		Stream.of(comboSampling, choiceOfSpectrumType, btnPlay).forEach(control -> control.setDisable(false));
		List<String> channelNames = IntStream.range(0, waveData.getInfo().getNbOfChannels())
						                            .mapToObj(i -> Channel.of(i, waveData.getInfo().getNbOfChannels()))
						                            .map(Channel::getName)
						                            .collect(Collectors.toList());
		channelNames.add("All");
		choiceOfChannel.setItems(FXCollections.observableArrayList(channelNames));
		if (!isListenerSet.get()) {
			isListenerSet.set(true);
			choiceOfChannel.getSelectionModel().selectedIndexProperty().addListener(
							(observable, oldValue, newValue) -> {
								plotSelectedChannels(newValue.intValue());
							});
			chartWave.setOnMouseMoved(this::stateMousePosition);
			Stream.of(limMin, limMax, timeBar).forEach(TimeWindowLimit::addToChart);
			Stream.of(limMin, limMax).forEach(TimeWindowLimit::addEventHandlers);
			setLimitColor();
		}
		limMin.moveTo(0.);
		limMax.moveTo(waveData.getInfo().getDuration());

		choiceOfChannel.getSelectionModel().selectFirst();
	}

	private void showError(Exception e) {
		lblFileInfo.setText(e.getMessage());
	}

	private void setLimitColor() {
		IntStream.range(0, 2).forEach(i -> {
			Optional.ofNullable(chartWave.lookup(".default-color" + i + "" +
			                                     ".chart-series-line"))
							.ifPresent(line -> line.setStyle("-fx-stroke: #000000;"));

			Optional.ofNullable(chartWave.lookup(".default-color" + i +
			                                     ".chart-line-symbol"))
							.ifPresent(legend -> legend.setStyle("-fx-background-color: #000000;"));
		});
	}

	private void stateMousePosition(MouseEvent event) {
		StringBuilder builder = new StringBuilder()
						                        .append("t = ").append(waveCoordinates.xLogical(event))
						                        .append(", a(t) = ").append(waveCoordinates.xLogical(event));
		lblStatus.setText(builder.toString());
	}

	private void plotChannel(int chIdx) {
		Channel ch = Channel.of(chIdx, waveData.getInfo().getNbOfChannels());
		double[] wave = waveData.getWave(ch).wave();
		XYChart.Series series = new XYChart.Series();
		series.setName(ch.getName());
		String sampling = comboSampling.getValue().toString();
		int samplingFreq = scale;
		try {
			samplingFreq = Integer.valueOf(sampling);
		} catch (Exception fallBack) {
			comboSampling.setValue("Random");
			if (!sampling.equals("Random")) {
				LOG.warning(() -> "Cannot parse sampling frequency '" + comboSampling
								                                                        .getValue().toString() + "'. " +
				                  "Falling back to 'Random'");
				// return;
				sampling = "Random";
			}
		}
		List<Integer> sampleIndexes;
		if (sampling.equals("Random")) {
			int i = 0;
			sampleIndexes = new ArrayList((int) (samplingFreq * 0.6));
			while (i < waveData.getInfo().getNbOfFrames()) {
				sampleIndexes.add(i);
				i += Math.random() * samplingFreq;
			}
		} else {
			int inc = waveData.getInfo().getFrameRate() / samplingFreq;
			sampleIndexes = IntStream.range(0, (int) Math.floor(waveData.getInfo().getDuration()
			                                                    * samplingFreq))
							                .mapToObj(i -> i * inc)
							                .collect(Collectors.toList());
		}
		sampleIndexes.forEach(i ->
						                      series.getData().add(new XYChart.Data(
										                      (double) (i) / waveData.getInfo().getFrameRate(),
										                      wave[i])));

		chartWave.getData().add(series);
	}

}
