package wave.view;

import javafx.geometry.Point2D;
import javafx.scene.input.MouseEvent;

class ChartCoordinates {
	private final WaveViewController controller;
	private ChartCoordinates(WaveViewController controller) {
		this.controller = controller;
	}

	static ChartCoordinates of(WaveViewController controller) {
		return new ChartCoordinates(controller);
	}

	private Point2D scene(MouseEvent event) {
		return new Point2D(event.getSceneX(), event.getSceneY());
	}

	double xLogical(MouseEvent event) {
		return logical(scene(event)).getX();
	}

	double yLogical(MouseEvent event) {
		return logical(scene(event)).getY();
	}

	private Point2D logical(Point2D scene) {
		Point2D local = local(scene);
		return new Point2D(controller.xAxis.getValueForDisplay(local.getX()).doubleValue(),
							controller.yAxis.getValueForDisplay(local.getY()).doubleValue());
	}

	private Point2D logical(MouseEvent event) {
		return logical(scene(event));
	}

	private Point2D local(Point2D scene) {
		return new Point2D(controller.xAxis.sceneToLocal(scene).getX(),
							controller.yAxis.sceneToLocal(scene).getY());
	}
}
