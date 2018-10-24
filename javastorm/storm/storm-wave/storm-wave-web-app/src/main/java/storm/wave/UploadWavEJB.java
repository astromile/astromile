package storm.wave;

import org.primefaces.event.*;
import org.primefaces.model.*;

import javax.enterprise.context.*;
import javax.faces.application.*;
import javax.faces.context.*;
import javax.inject.*;
import java.io.*;
import java.nio.file.*;

@SessionScoped
@Named("uploadWave")
public class UploadWavEJB implements Serializable {

	public void onUpload(FileUploadEvent event) {
		try {
			saveFile(event.getFile());
			FacesMessage message = new FacesMessage("Successful",
					event.getFile().getFileName() + " is uploaded");
			FacesContext.getCurrentInstance().addMessage(null, message);
		} catch (IOException e) {
			FacesMessage message = new FacesMessage("Error",
					event.getFile().getFileName() + " cannot be saved: " + e);
			FacesContext.getCurrentInstance().addMessage(null, message);
		}
	}

	private void saveFile(UploadedFile file) throws IOException {
		Path folder = Paths.get("c:/tmp/wave/upload");
		String fileName = file.getFileName();
		Path filePath = Files.createTempFile(folder, fileName + '-', ".upload");
		try (InputStream input = file.getInputstream()) {
			Files.copy(input, filePath, StandardCopyOption.REPLACE_EXISTING);
		} catch (IOException ioe) {
			throw ioe;
		}
	}
}
