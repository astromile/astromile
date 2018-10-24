package storm.jee;

import javax.ejb.*;

@Remote
public interface TestRemote {
	int answerTheMainQuestion();
}
