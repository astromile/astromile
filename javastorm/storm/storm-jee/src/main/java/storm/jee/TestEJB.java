package storm.jee;

import javax.ejb.*;

@Stateless
@LocalBean
public class TestEJB implements TestRemote {
	@Override
	public int answerTheMainQuestion() {
		return 42;
	}
}
