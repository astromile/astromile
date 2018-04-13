package wave.util;

import java.util.function.Supplier;

public interface Ensure {

    public static void that(boolean condition, Supplier<String> errorMessage){
        if(!condition){
            throw new RuntimeException(errorMessage.get());
        }
    }
}
