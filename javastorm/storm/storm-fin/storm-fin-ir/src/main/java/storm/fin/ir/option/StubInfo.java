package storm.fin.ir.option;

import java.time.*;

public final class StubInfo {
	enum Type {Short, Long}

	private final Type initialStub, finalStub;
	private final LocalDate rollingDate;

	private StubInfo(LocalDate rollingDate, Type initialStub, Type finalStub) {
		this.initialStub = initialStub;
		this.finalStub = finalStub;
		this.rollingDate = rollingDate;
	}

	public StubInfo of(LocalDate rollingDate, Type initialStub, Type finalStub) {
		return new StubInfo(rollingDate, initialStub, finalStub);
	}

	public Type getInitialStub() {
		return initialStub;
	}

	public Type getFinalStub() {
		return finalStub;
	}

	public LocalDate getRollingDate() {
		return rollingDate;
	}
}
