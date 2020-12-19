package sandarukasa.SKTG;

import org.telegram.telegrambots.TelegramBotsApi;
import org.telegram.telegrambots.api.objects.Message;
import org.telegram.telegrambots.exceptions.TelegramApiException;

import java.util.ResourceBundle;

public class BetaLupi extends AbstractTelegramBot {
    public BetaLupi(TelegramBotsApi telegramBotsApi, ResourceBundle tokens) throws TelegramApiException {
        super(telegramBotsApi, tokens);
    }

    public BetaLupi(ResourceBundle tokens) throws TelegramApiException {
        super(tokens);
    }

    @Override
    protected String getLocalID() {
        return "testbot";
    }

    @CommandHandler(commandName = "mp3", commandAliases = {})
    protected final void oggToMp3(Message message) {

    }
}
