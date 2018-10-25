package storm.wave;

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
