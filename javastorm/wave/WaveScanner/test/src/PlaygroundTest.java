import org.junit.*;

import java.util.logging.Logger;
import java.util.stream.IntStream;

public class PlaygroundTest {
    private final static Logger LOGGER = Logger.getLogger(PlaygroundTest.class.getName());


    @Test
    public void testMaxNumbers(){
        LOGGER.info("Type\t\t\tMaximum Value");
        LOGGER.info("int\t\t\t" + Integer.MAX_VALUE);
        LOGGER.info("=> " + Integer.MAX_VALUE/44000/60/60 + " hours");
    }

    @Test
    public void testEmptyRange(){
        IntStream.range(0,0).forEach(Integer::toString);
    }

}
