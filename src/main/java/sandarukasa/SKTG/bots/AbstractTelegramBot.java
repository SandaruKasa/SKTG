package sandarukasa.SKTG.bots;

import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.api.methods.ActionType;
import org.telegram.telegrambots.meta.api.methods.AnswerCallbackQuery;
import org.telegram.telegrambots.meta.api.methods.GetFile;
import org.telegram.telegrambots.meta.api.methods.commands.SetMyCommands;
import org.telegram.telegrambots.meta.api.methods.send.SendAudio;
import org.telegram.telegrambots.meta.api.methods.send.SendChatAction;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.methods.send.SendPhoto;
import org.telegram.telegrambots.meta.api.objects.*;
import org.telegram.telegrambots.meta.api.objects.commands.BotCommand;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.meta.generics.BotSession;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;
import sandarukasa.SKTG.bots.handler_annotations.CommandHandler;
import sandarukasa.SKTG.bots.handler_annotations.TextTriggerHandler;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.time.Duration;
import java.time.Instant;
import java.util.*;

public abstract class AbstractTelegramBot extends TelegramLongPollingBot {
    protected final Map<String, Method> commandHandlers;
    protected final List<Method> textTriggerHandlers;
    protected final Instant startTime = Instant.now();
    private final String USERNAME;
    private final String TOKEN;
    private final BotSession botSession;

    public AbstractTelegramBot(TelegramBotsApi telegramBotsApi, ResourceBundle tokens) throws TelegramApiException {
        super();
        TOKEN = tokens.getString(getLocalID());
        USERNAME = getMe().getUserName();
        botSession = telegramBotsApi.registerBot(this);
        commandHandlers = new LinkedHashMap<>();
        textTriggerHandlers = new LinkedList<>();
        setupHandlers(this.getClass().getSuperclass(), this.getClass());
    }

    public AbstractTelegramBot(ResourceBundle tokens) throws TelegramApiException {
        this(new TelegramBotsApi(DefaultBotSession.class), tokens);
    }

    protected static List<MessageEntity> getEntities(Message message) {
        List<MessageEntity> textEntities = message.getEntities();
        return (textEntities != null && !textEntities.isEmpty()) ? textEntities : message.getCaptionEntities();
    }

    private void setupHandlers(Class<?>... classesWithHandlers) throws TelegramApiException {
        List<BotCommand> myCommands = new LinkedList<>();
        for (Class<?> classWithCommandHandlers : classesWithHandlers) {
            for (Method method : classWithCommandHandlers.getDeclaredMethods()) {
                if (method.isAnnotationPresent(CommandHandler.class)) {
                    CommandHandler commandHandlerAnnotation = method.getAnnotation(CommandHandler.class);
                    commandHandlers.put(commandHandlerAnnotation.commandName().toLowerCase(), method);
                    if (commandHandlerAnnotation.availableInTheList()) {
                        myCommands.add(new BotCommand(commandHandlerAnnotation.commandName(), commandHandlerAnnotation.description()));
                    }
                    for (String commandAlias : commandHandlerAnnotation.commandAliases()) {
                        commandHandlers.put(commandAlias.toLowerCase(), method);
                    }
                }
                if (method.isAnnotationPresent(TextTriggerHandler.class)) {
                    textTriggerHandlers.add(method);
                }
            }
        }
        sendApiMethod(new SetMyCommands(myCommands));
    }

    protected String getString(String key, String languageCode) {
        return languageCode != null ?
                ResourceBundle.getBundle(getLocalID(), Locale.forLanguageTag(languageCode)).getString(key) :
                ResourceBundle.getBundle(getLocalID()).getString(key);
    }

    protected String getString(String key, User targetLanguageUser) {
        return targetLanguageUser != null ?
                getString(key, targetLanguageUser.getLanguageCode()) :
                getString(key, (String) null);
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
            final String text = message.getText();
            if (command != null) {
                Method commandHandler = commandHandlers.get(command.toLowerCase());
                if (commandHandler != null) {
                    try {
                        commandHandler.invoke(this, message);
                    } catch (IllegalAccessException | InvocationTargetException e) {
                        e.printStackTrace();
                    }
                }
            } else if (text != null) {
                for (Method textTriggerHandler : textTriggerHandlers) {
                    if (text.matches(textTriggerHandler.getAnnotation(TextTriggerHandler.class).regex())) {
                        try {
                            textTriggerHandler.invoke(this, message);
                        } catch (IllegalAccessException | InvocationTargetException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
        } else if (update.hasCallbackQuery()) {
            onCallbackQueryReceived(update.getCallbackQuery());
        }
    }

    protected void onCallbackQueryReceived(CallbackQuery callbackQuery) {
        try {
            sendApiMethod(new AnswerCallbackQuery(callbackQuery.getId()));
        } catch (TelegramApiException ignored) {
        }
    }

    @Override
    public void onUpdatesReceived(List<Update> updates) {
        updates.forEach(update -> new Thread(() -> this.onUpdateReceived(update)).start());
    }

    @CommandHandler(commandName = "help", commandAliases = {"start"}, availableInTheList = true,
            description = "Displays help message")
    protected void help(Message message) throws TelegramApiException {
        replyWithMessage(message, SendMessage.builder().text(getString("help", message.getFrom())).parseMode("html"));
    }

    @CommandHandler(commandName = "github", commandAliases = {}, availableInTheList = false,
            description = "GitHub repo link")
    protected void github(Message message) throws TelegramApiException {
        replyWithMessage(message, SendMessage.builder().text("https://github.com/SandaruKasa/SKTG/tree/java").disableWebPagePreview(true));
    }

    @CommandHandler(commandName = "uptime", commandAliases = {}, availableInTheList = false,
            description = "Bot uptime")
    protected void uptime(Message message) throws TelegramApiException {
        final Duration uptime = Duration.between(startTime, Instant.now());
        final String days = String.valueOf(uptime.toDays());
        replyWithText(message, String.format("%s%02d:%02d:%02d", switch (days) {
            case "0" -> "";
            case "1" -> "1 day, ";
            default -> days + " days, ";
        }, uptime.toHoursPart(), uptime.toMinutesPart(), uptime.toSecondsPart()));
    }

    protected java.io.File downloadFileById(String fileId) throws TelegramApiException {
        return downloadFile(execute(new GetFile(fileId)));
    }

    protected void sendChatAction(Long chatId, ActionType actionType) {
        try {
            sendApiMethod(new SendChatAction(String.valueOf(chatId), actionType.toString()));
        } catch (TelegramApiException ignored) {
        }
    }


    protected Message replyWithLocalizedText(Message replyToMessage, String key) throws TelegramApiException {
        return replyWithText(replyToMessage, getString(key, replyToMessage.getFrom().getLanguageCode()));
    }

    protected Message replyWithText(Message replyToMessage, String text) throws TelegramApiException {
        return replyWithMessage(replyToMessage, SendMessage.builder().text(text));
    }

    protected Message replyWithMessage(Message replyToMessage, SendMessage.SendMessageBuilder sendMessageBuilder)
            throws TelegramApiException {
        Message result;
        try {
            result = sendApiMethod(sendMessageBuilder.chatId(String.valueOf(replyToMessage.getChatId())).replyToMessageId(replyToMessage.getMessageId()).build());
        } catch (TelegramApiException e) {
            result = sendApiMethod(sendMessageBuilder.replyToMessageId(null).build());
        }
        return result;
    }

    protected Message replyWithAudio(Message replyToMessage, SendAudio.SendAudioBuilder sendAudioBuilder)
            throws TelegramApiException {
        Message result;
        try {
            result = execute(sendAudioBuilder.chatId(String.valueOf(replyToMessage.getChatId())).replyToMessageId(replyToMessage.getMessageId()).build());
        } catch (TelegramApiException e) {
            result = execute(sendAudioBuilder.replyToMessageId(null).build());
        }
        return result;
    }

    protected Message replyWithPhoto(Message replyToMessage, SendPhoto.SendPhotoBuilder sendPhotoBuilder)
            throws TelegramApiException {
        Message result;
        try {
            result = execute(sendPhotoBuilder.chatId(String.valueOf(replyToMessage.getChatId())).replyToMessageId(replyToMessage.getMessageId()).build());
        } catch (TelegramApiException e) {
            result = execute(sendPhotoBuilder.replyToMessageId(null).build());
        }
        return result;
    }
}
