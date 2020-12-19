package sandarukasa.SKTG.bots.handler_annotations;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface CommandHandler {
    String commandName();

    String[] commandAliases();

    boolean availableInTheList();

    String description();
}
