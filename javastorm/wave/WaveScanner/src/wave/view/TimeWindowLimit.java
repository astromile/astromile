package wave.view;

import javafx.scene.Cursor;
import javafx.scene.Node;
import javafx.scene.chart.XYChart;

class TimeWindowLimit {
	private WaveViewController waveViewController;
	double x;
	private double yMin;
	private double yMax;
	final XYChart.Series series;
	private boolean eventHandlersSet = false;
	private boolean dragging = false;
	private boolean addedToChart = false;

	TimeWindowLimit(WaveViewController waveViewController, double x) {
		this.waveViewController = waveViewController;
		this.x = x;
		series = new XYChart.Series();
		series.setName("Limit");
		series.getData().add(new XYChart.Data(x, -1.));
		series.getData().add(new XYChart.Data(x, +1.));
	}

	void addEventHandlers() {
		if (!eventHandlersSet) {
			eventHandlersSet = true;
			setMouseHoverHandlers();
			setMouseDragHandlers();
		}
	}

	private void setMouseDragHandlers() {
		series.getNode().setOnMousePressed(event -> event.setDragDetect(true));
		series.getNode().setOnDragDetected(event -> dragging = true);
		series.getNode().setOnMouseDragged(event -> {
			double newX = waveViewController.waveCoordinates.xLogical(event);
			double dx = newX - x;
			moveTo(newX);
			if (this == waveViewController.limMin) {
				waveViewController.limMax.moveTo(waveViewController.limMax.x + dx);
			}
			waveViewController.lblStatus.setText(
								"x_" + (waveViewController.selectedLimit == waveViewController.limMin ? "min" : "max")
													+ " = " + newX);
			event.setDragDetect(false);
		});
		series.getNode().setOnMouseReleased(event -> {
			if (dragging) {
				dragging = false;
				if (waveViewController.limMin.x > waveViewController.limMax.x) {
					TimeWindowLimit tmp = waveViewController.limMin;
					waveViewController.limMin = waveViewController.limMax;
					waveViewController.limMax = tmp;
				}
				int channel = waveViewController.choiceOfChannel.getSelectionModel().getSelectedIndex();
				waveViewController.plotChannelsSpectrum(waveViewController.selectChannels(channel));
			}
		});
	}

	private void setMouseHoverHandlers() {
		series.getNode().setOnMouseEntered(event -> {
			((Node) (event.getSource())).setCursor(Cursor.H_RESIZE);
		});
		series.getNode().setOnMouseExited(event -> {
			((Node) (event.getSource())).setCursor(Cursor.DEFAULT);
		});
	}

	void moveTo(double x) {
		this.x = Math.min(Math.max(0., x), waveViewController.waveData.getInfo().getDuration());
		series.getData().set(0, new XYChart.Data(this.x, -1.));
		series.getData().set(1, new XYChart.Data(this.x, +1.));
	}

	void addToChart() {
		WaveViewController.LOG.info("Plotting limit " + (this == waveViewController.limMin
							                                                 ? "MIN" : (this == waveViewController.limMax ? "MAX" : "Time Bar")));
		if (!addedToChart) {
			addedToChart = false;
			waveViewController.chartWave.getData().add(series);
		}
	}

}
