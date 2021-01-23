package sandarukasa.SKTG.bots.impdro;

import org.telegram.telegrambots.meta.api.objects.Chat;
import org.telegram.telegrambots.meta.api.objects.Message;
import org.telegram.telegrambots.meta.api.objects.User;
import sandarukasa.SKTG.SQLiteDatabase;

import java.nio.file.Path;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;

public class ActivityCounter implements AutoCloseable {
    private final SQLiteDatabase sqldb;

    public ActivityCounter(Path containingDirectory) {
        try {
            sqldb = new SQLiteDatabase(Path.of(containingDirectory.toString(), "ActivityCounter.db").toString());
            sqldb.executeStatement("CREATE TABLE if not exists users (id INTEGER PRIMARY KEY, firstname text, username text, lastname text);");
            sqldb.executeStatement("CREATE TABLE if not exists chats (id INTEGER PRIMARY KEY, title text, username text);");
            sqldb.executeStatement("CREATE TABLE if not exists counters (user INTEGER, chat INTEGER, counter INTEGER);");
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public void update(User user) {
        try (final PreparedStatement query = sqldb.prepareStatement("SELECT firstname, username, lastname FROM users WHERE id = ?;")) {
            query.setInt(1, user.getId());
            try (final ResultSet resultSet = query.executeQuery()) {
                if (!resultSet.next()) {
                    try (final PreparedStatement preparedStatement =
                                 sqldb.prepareStatement("INSERT INTO users(id, firstname, username, lastname) VALUES (?, ?, ?, ?);")) {
                        preparedStatement.setInt(1, user.getId());
                        preparedStatement.setString(2, user.getFirstName());
                        preparedStatement.setString(3, user.getUserName());
                        preparedStatement.setString(4, user.getLastName());
                        preparedStatement.execute();
                    }
                } else if (!user.getFirstName().equals(resultSet.getString("firstname")) ||
                        Objects.equals(user.getUserName(), resultSet.getString("username")) ||
                        Objects.equals(user.getLastName(), resultSet.getString("lastname"))
                ) {
                    try (final PreparedStatement preparedStatement =
                                 sqldb.prepareStatement("UPDATE users SET firstname = ?, username = ?, lastname=? WHERE id = ?;")) {
                        preparedStatement.setString(1, user.getFirstName());
                        preparedStatement.setString(2, user.getUserName());
                        preparedStatement.setString(3, user.getLastName());
                        preparedStatement.setInt(4, user.getId());
                        preparedStatement.execute();
                    }
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public void update(Chat chat) {
        if (!chat.isUserChat()) {
            try (final PreparedStatement query = sqldb.prepareStatement("SELECT title, username FROM chats WHERE id = ?;")) {
                query.setLong(1, chat.getId());
                try (final ResultSet resultSet = query.executeQuery()) {
                    if (!resultSet.next()) {
                        try (final PreparedStatement preparedStatement =
                                     sqldb.prepareStatement("INSERT INTO chats(id, title, username) VALUES (?, ?, ?);")) {
                            preparedStatement.setLong(1, chat.getId());
                            preparedStatement.setString(2, chat.getTitle());
                            preparedStatement.setString(3, chat.getUserName());
                            preparedStatement.execute();
                        }
                    } else if (!chat.getTitle().equals(resultSet.getString("title")) || Objects.equals(chat.getUserName(),
                            resultSet.getString("username"))) {
                        try (final PreparedStatement preparedStatement =
                                     sqldb.prepareStatement("UPDATE chats SET title = ?, username = ? WHERE id = ?;")) {
                            preparedStatement.setString(1, chat.getTitle());
                            preparedStatement.setString(2, chat.getUserName());
                            preparedStatement.setLong(3, chat.getId());
                            preparedStatement.execute();
                        }
                    }
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public void update(Message message) {
        new Thread(() -> update(message.getFrom())).start();
        new Thread(() -> update(message.getChat())).start();
    }

    public void increase(Message message) {
        increase(message.getFrom(), message.getChat());
    }

    public User getUserInfo(int id) throws SQLException {
        try (final PreparedStatement preparedStatement =
                     sqldb.prepareStatement("SELECT firstname, username, lastname FROM users WHERE id = ?;")) {
            preparedStatement.setInt(1, id);
            try (final ResultSet resultSet = preparedStatement.executeQuery()) {
                final User result = new User(id, resultSet.getString("firstname"), false);
                result.setUserName(resultSet.getString("username"));
                result.setLastName(resultSet.getString("lastname"));
                return result;
            }
        }
    }


    public void increase(User user, Chat chat) {
        try (final PreparedStatement preparedStatement = sqldb.prepareStatement("SELECT counter FROM counters WHERE user = ? AND chat = ?;")) {
            preparedStatement.setInt(1, user.getId());
            preparedStatement.setLong(2, chat.getId());
            try (final ResultSet resultSet = preparedStatement.executeQuery()) {
                if (resultSet.next()) {
                    final int counter = resultSet.getInt("counter");
                    try (final PreparedStatement preparedStatement1 = sqldb.prepareStatement(
                            "UPDATE counters SET counter = ? WHERE user = ? AND chat = ?;"
                    )) {
                        preparedStatement1.setInt(1, counter + 1);
                        preparedStatement1.setInt(2, user.getId());
                        preparedStatement1.setLong(3, chat.getId());
                        preparedStatement1.execute();
                    }
                } else {
                    try (final PreparedStatement preparedStatement1 = sqldb.prepareStatement(
                            "INSERT into counters (user, chat, counter) VALUES (?, ?, 1);"
                    )) {
                        preparedStatement1.setInt(1, user.getId());
                        preparedStatement1.setLong(2, chat.getId());
                        preparedStatement1.execute();
                    }
                }
            }
        } catch (SQLException ignored) {
        }
    }

    public Chat getChatInfo(long id) throws SQLException {
        try (final PreparedStatement preparedStatement =
                     sqldb.prepareStatement("SELECT title, username FROM chats WHERE id = ?;")) {
            preparedStatement.setLong(1, id);
            try (final ResultSet resultSet = preparedStatement.executeQuery()) {
                final Chat result = new Chat(id, "not a user");
                result.setTitle(resultSet.getString("title"));
                return result;
            }
        }
    }

    public List<UserStatsEntry> getUserStats(User user) throws SQLException {
        final LinkedList<UserStatsEntry> result = new LinkedList<>();
        try (final PreparedStatement preparedStatement =
                     sqldb.prepareStatement("SELECT chat, counter FROM counters WHERE user = ? ORDER BY counter DESC;")) {
            preparedStatement.setInt(1, user.getId());
            try (final ResultSet resultSet = preparedStatement.executeQuery()) {
                while (resultSet.next()) {
                    result.add(new UserStatsEntry(resultSet.getLong("chat"), resultSet.getInt("counter")));
                }
            }
        }
        return result;
    }

    public List<ChatStatsEntry> getChatStats(Chat chat) throws SQLException {
        assert !chat.isUserChat();
        final LinkedList<ChatStatsEntry> result = new LinkedList<>();
        try (final PreparedStatement preparedStatement =
                     sqldb.prepareStatement("SELECT user, counter FROM counters WHERE chat = ? ORDER BY counter DESC;")) {
            preparedStatement.setLong(1, chat.getId());
            try (final ResultSet resultSet = preparedStatement.executeQuery()) {
                while (resultSet.next()) {
                    result.add(new ChatStatsEntry(resultSet.getInt("user"), resultSet.getInt("counter")));
                }
            }
        }
        return result;
    }

    public static record UserStatsEntry(long chatId, int counter) {
    }

    public static record ChatStatsEntry(int userId, int counter) {
    }


    @Override
    public void close() throws SQLException {
        sqldb.close();
    }
}
