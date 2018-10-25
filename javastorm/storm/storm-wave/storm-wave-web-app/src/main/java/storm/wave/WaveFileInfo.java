package storm.wave;

import java.time.*;

public interface WaveFileInfo {

	String getName();

	long getSize();

	LocalDateTime getUploadTime();

	static WaveFileInfo of(String name, long size, LocalDateTime uploaded) {
		return new WaveFileInfo() {
			@Override
			public String getName() {
				return name;
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
