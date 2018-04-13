package wave;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

/**
 * Scans WAV file wave audio format and recognises notes, chords, etc.
 */
public class WaveScannerApp extends Application {

    @Override
    public void start(Stage primaryStage) throws Exception{
        Parent root = FXMLLoader.load(getClass().getResource("view/WaveView.fxml"));
        primaryStage.setTitle("WaveData Scanner");
        primaryStage.setScene(new Scene(root, 600, 600));
        primaryStage.show();
    }


    public static void main(String[] args) {
        launch(args);
    }
}

//    v: Load file
//    v: Read in waves of all channels
// TODO: play file (sub tasks to follow...)
// TODO: FFT to recognize notes
// TODO: static output of waves themselves and spectral representation
// TODO: dynamic output of waves and spectral representation during playing wav file