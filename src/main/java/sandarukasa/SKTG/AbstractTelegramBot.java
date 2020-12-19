package sandarukasa.SKTG;

import org.telegram.telegrambots.TelegramBotsApi;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.exceptions.TelegramApiException;
import org.telegram.telegrambots.generics.BotSession;

import java.util.ResourceBundle;

public abstract class AbstractTelegramBot extends TelegramLongPollingBot {
    private final String USERNAME;
    private final String TOKEN;
    private final BotSession botSession;

    public AbstractTelegramBot(TelegramBotsApi telegramBotsApi, ResourceBundle tokens) throws TelegramApiException {
        super();
        TOKEN = tokens.getString(getLocalID());
        USERNAME = getMe().getUserName();
        botSession = telegramBotsApi.registerBot(this);

    }

    protected String getString(String key, String languageCode) {
        return "";
    }

    @Override
    public String getBotUsername() {
        return USERNAME;
    }

    @Override
    public String getBotToken() {
        return TOKEN;
    }

    protected abstract String getLocalID();

    public BotSession getBotSession() {
        return botSession;
    }
}
