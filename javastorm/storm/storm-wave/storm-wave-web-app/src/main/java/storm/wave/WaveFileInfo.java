package storm.wave;

import java.nio.file.*;
import java.time.*;

public interface WaveFileInfo {

	String getName();

	Path getPath();

	long getSize();

	LocalDateTime getUploadTime();

	static WaveFileInfo of(String name, Path path, long size, LocalDateTime uploaded) {
		return new WaveFileInfo() {
			@Override
			public String getName() {
				return name;
			}

			@Override
			public Path getPath() {
				return path;
			}

			@Override
			public long getSize() {
				return size;
			}

			@Override
			public LocalDateTime getUploadTime() {
				return uploaded;
			}

			@Override
			public String toString() {
				return getName() + " [" + getSize() + "B] @ " + getUploadTime().toLocalDate();
			}

		};
	}


}
