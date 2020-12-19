package sandarukasa.SKTG;

import org.telegram.telegrambots.TelegramBotsApi;
import org.telegram.telegrambots.api.methods.GetFile;
import org.telegram.telegrambots.api.methods.send.SendAudio;
import org.telegram.telegrambots.api.methods.send.SendMessage;
import org.telegram.telegrambots.api.objects.Message;
import org.telegram.telegrambots.api.objects.MessageEntity;
import org.telegram.telegrambots.api.objects.Update;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.exceptions.TelegramApiException;
import org.telegram.telegrambots.generics.BotSession;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.List;
import java.util.ResourceBundle;

public abstract class AbstractTelegramBot extends TelegramLongPollingBot {
    private final String USERNAME;
    private final String TOKEN;
    private final BotSession botSession;
    protected final HashMap<String, Method> commandHandlers;

    @Override
    public void onUpdatesReceived(List<Update> updates) {
        updates.forEach(UpdateProcessor::new);
    }

    public AbstractTelegramBot(TelegramBotsApi telegramBotsApi, ResourceBundle tokens) throws TelegramApiException {
        super();
        TOKEN = tokens.getString(getLocalID());
        USERNAME = getMe().getUserName();
        botSession = telegramBotsApi.registerBot(this);
        commandHandlers = new HashMap<>();
        for (Method method : this.getClass().getDeclaredMethods()) {
            if (method.isAnnotationPresent(CommandHandler.class)) {
                CommandHandler commandHandlerAnnotation = method.getAnnotation(CommandHandler.class);
                commandHandlers.put(commandHandlerAnnotation.commandName(), method);
                for (String commandAlias : commandHandlerAnnotation.commandAliases()) {
                    commandHandlers.put(commandAlias, method);
                }
            }
        }
    }

    public AbstractTelegramBot(ResourceBundle tokens) throws TelegramApiException {
        this(new TelegramBotsApi(), tokens);
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

    protected static List<MessageEntity> getEntities(Message message) {
        List<MessageEntity> textEntities = message.getEntities();
        return (textEntities != null && !textEntities.isEmpty()) ? textEntities : message.getCaptionEntities();
    }

    protected String getCommand(Message message) {
        List<MessageEntity> entities = getEntities(message);
        if (entities != null) {
            for (MessageEntity entity : entities) {
                if ("bot_command".equalsIgnoreCase(entity.getType())) {
                    String command_text = entity.getText();
                    String[] a = command_text.split("@");
                    try {
                        return getBotUsername().equalsIgnoreCase(a[1]) ? a[0].substring(1) : null;
                    } catch (ArrayIndexOutOfBoundsException e) {
                        return a[0].substring(1);
                    }
                }
            }
        }
        return null;
    }

    @Override
    public void onUpdateReceived(Update update) {
        if (update.hasMessage()) {
            final Message message = update.getMessage();
            final String command = getCommand(message);
            if (command != null) {
                Method commandHandler = commandHandlers.get(command.toLowerCase());
                try {
                    commandHandler.invoke(this, message);
                } catch (IllegalAccessException | InvocationTargetException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    protected class UpdateProcessor extends Thread {
        protected final Update update;

        public UpdateProcessor(Update update) {
            this.update = update;
            this.start();
        }

        @Override
        public void run() {
            AbstractTelegramBot.this.onUpdateReceived(update);
        }
    }

    protected java.io.File downloadFileById(String fileId) throws TelegramApiException {
        return downloadFile(execute(new GetFile().setFileId(fileId)));
    }

    protected Message replyWithAMessage(Message replyToMessage, SendMessage sendMessage) throws TelegramApiException {
        Message result;
        try {
            result = sendApiMethod(sendMessage.setChatId(replyToMessage.getChatId()).setReplyToMessageId(replyToMessage.getMessageId()));
        } catch (TelegramApiException e) {
            result = sendApiMethod(sendMessage.setReplyToMessageId(null));
        }
        return result;
    }

    protected Message replyWithAnAudio(Message replyToMessage, SendAudio sendAudio) throws TelegramApiException {
        Message result;
        try {
            result = sendAudio(sendAudio.setChatId(replyToMessage.getChatId()).setReplyToMessageId(replyToMessage.getMessageId()));
        } catch (TelegramApiException e) {
            result = sendAudio(sendAudio.setReplyToMessageId(null));
        }
        return result;
    }
}
