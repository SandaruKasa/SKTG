package sandarukasa.SKTG.bots;

import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.methods.updatingmessages.EditMessageText;
import org.telegram.telegrambots.meta.api.objects.Chat;
import org.telegram.telegrambots.meta.api.objects.Message;
import org.telegram.telegrambots.meta.api.objects.User;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import sandarukasa.SKTG.bots.handler_annotations.CommandHandler;
import sandarukasa.SKTG.bots.impdro.ActivityCounter;

import java.sql.SQLException;
import java.util.List;
import java.util.ResourceBundle;

public class ImperialDrone extends AbstractTelegramBot {
    private final ActivityCounter activityCounter = new ActivityCounter(workingDirectory);

    public ImperialDrone(TelegramBotsApi telegramBotsApi, ResourceBundle tokens) throws TelegramApiException {
        super(telegramBotsApi, tokens);
    }

    public ImperialDrone(ResourceBundle tokens) throws TelegramApiException {
        super(tokens);
    }

    @Override
    protected String getLocalID() {
        return "testbot";
    }

    @CommandHandler(commandName = "counted_command", commandAliases = {}, availableInTheList = true,
            description = "Increase activity counter")
    protected void countedCommand(Message message) throws TelegramApiException {
        new Thread(() -> activityCounter.increase(message)).start();
        replyWithLocalizedText(message, "done");
    }

    @CommandHandler(commandName = "get_stats", commandAliases = {}, availableInTheList = true,
            description = "Get activity stats")
    protected void getStats(Message message) throws TelegramApiException {
        try {
            int position = 1;
            if (message.getChat().isUserChat()) {
                final List<ActivityCounter.UserStatsEntry> userStats = activityCounter.getUserStats(message.getFrom());
                if (userStats.isEmpty()) {
                    replyWithLocalizedText(message, "no_user_stats");
                } else {
                    final StringBuilder textBuilder = new StringBuilder(getLocalized("user_stats_header", message.getFrom()));
                    for (ActivityCounter.UserStatsEntry entry : userStats) {
                        if (entry.chatId() == message.getChatId()) {
                            appendUser(textBuilder, message.getFrom().getId(), entry.counter(), position++);
                        } else {
                            appendChat(textBuilder, entry.chatId(), entry.counter(), position++);
                        }
                    }
                    replyWithMessage(message, SendMessage.builder().text(textBuilder.toString()).parseMode("HTML").disableWebPagePreview(true));
                }
            } else {
                final List<ActivityCounter.ChatStatsEntry> chatStats = activityCounter.getChatStats(message.getChat());
                if (chatStats.isEmpty()) {
                    replyWithLocalizedText(message, "no_chat_stats");
                } else {
                    final StringBuilder textBuilder = new StringBuilder(getLocalized("chat_stats_header", message.getFrom()));
                    for (ActivityCounter.ChatStatsEntry entry : chatStats) {
                        appendUser(textBuilder, entry.userId(), entry.counter(), position++);
                    }
                    final Message placeholder = replyWithLocalizedText(message, "loading");
                    sendApiMethod(EditMessageText.builder().text(textBuilder.toString()).parseMode("HTML")
                            .chatId(placeholder.getChatId().toString()).messageId(placeholder.getMessageId()).build());
                }
            }
        } catch (SQLException e) {
            replyWithLocalizedText(message, "unknown_error");
            throw new RuntimeException(e);
        }
    }

    private void appendUser(StringBuilder stringBuilder, int userId, int counter, int position) throws SQLException {
        final User user = activityCounter.getUserInfo(userId);
        stringBuilder.append("\n").append(position).append(". <b>").append(counter)
                .append("</b> — <a href=\"tg://user?id=").append(user.getId()).append("\">")
                .append(htmlEscape(user.getFirstName()));
        if (user.getLastName() != null) {
            stringBuilder.append(" ").append(htmlEscape(user.getLastName()));

        }
        stringBuilder.append("</a>");
    }

    private void appendChat(StringBuilder stringBuilder, long chatId, int counter, int position) throws SQLException {
        final Chat chat = activityCounter.getChatInfo(chatId);
        final String username = chat.getUserName();
        stringBuilder.append("\n").append(position).append(". <b>").append(counter).append("</b> — ");
        if (username != null) {
            stringBuilder.append("<a href=\"https://t.me/").append(username).append("\">")
                    .append(htmlEscape(chat.getTitle())).append("</a>");
        } else {
            stringBuilder.append(htmlEscape(chat.getTitle()));
        }
    }

    @Override
    public void onMessageReceived(Message message) {
        activityCounter.update(message);
        super.onMessageReceived(message);
    }

    @Override
    public void onEditedMessageReceived(Message message) {
        activityCounter.update(message);
    }

    @Override
    public void close() {
        super.close();
        try {
            activityCounter.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
