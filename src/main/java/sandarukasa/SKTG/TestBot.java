package sandarukasa.SKTG;

import org.telegram.telegrambots.TelegramBotsApi;
import org.telegram.telegrambots.api.methods.send.SendMessage;
import org.telegram.telegrambots.api.objects.Message;
import org.telegram.telegrambots.api.objects.Update;
import org.telegram.telegrambots.exceptions.TelegramApiException;

import java.util.ResourceBundle;

public class TestBot extends AbstractTelegramBot {
    public TestBot(TelegramBotsApi telegramBotsApi, ResourceBundle tokens) throws TelegramApiException {
        super(telegramBotsApi, tokens);
    }

    @Override
    protected String getLocalID() {
        return "testbot";
    }

    @Override
    public void onUpdateReceived(Update update) {
        Message message = update.getMessage();
        String messageText;
        if (message != null && (messageText = message.getText()) != null) {
            if (messageText.toLowerCase().equals("stop")) {
                this.getBotSession().stop();
            } else {
                SendMessage reply = new SendMessage().setText(messageText).setChatId(message.getChatId())
                        .setReplyToMessageId(message.getMessageId());
                try {
                    sendApiMethod(reply);
                } catch (TelegramApiException e) {
                    e.printStackTrace(System.out);
                }
            }
        }
    }
}
