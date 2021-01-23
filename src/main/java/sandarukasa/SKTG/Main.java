package sandarukasa.SKTG;

import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import sandarukasa.SKTG.bots.AbstractTelegramBot;
import sandarukasa.SKTG.bots.ImperialDrone;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.ResourceBundle;

public class Main {
    private static final ResourceBundle TOKENS = ResourceBundle.getBundle("tokens");

    public static void main(String[] args) throws TelegramApiException {
        //todo logging
//        final List<AbstractTelegramBot> bots = List.of(new BetaLupi(TOKENS), new ImperialDrone(TOKENS));
        final List<AbstractTelegramBot> bots = List.of(new ImperialDrone(TOKENS));
        System.out.println("Started");
        try {
            while (true) {
                try {
                    if (Files.deleteIfExists(Path.of("stop"))) {
                        break;
                    }
                } catch (IOException ignored) {
                }
                Thread.sleep(1000);
            }
        } catch (InterruptedException ignored) {
        }
        System.out.println("Stopping");
        bots.forEach(AbstractTelegramBot::close);
    }
}
