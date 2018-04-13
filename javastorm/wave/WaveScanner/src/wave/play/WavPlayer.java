package wave.play;

import sun.audio.AudioPlayer;
import sun.audio.AudioStream;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;

public interface WavPlayer {
	void play() throws IOException;
	static WavPlayer of(String wavFileName){
		return ()->{
			{
				InputStream in = new FileInputStream(wavFileName);

				// create an audiostream from the inputstream
				AudioStream audioStream = new AudioStream(in);

				// play the audio clip with the audioplayer class
				AudioPlayer.player.start(audioStream);
			}
		};
	}
}
