package sandarukasa.SKTG;

import java.sql.*;

public class SQLiteDatabase implements AutoCloseable {
    private final Connection connection;
    private final Statement statement;

    public SQLiteDatabase(String url) throws SQLException {
        statement = (connection = DriverManager.getConnection("jdbc:sqlite:" + url)).createStatement();
    }

    public boolean executeStatement(String statement) throws SQLException {
        synchronized (this.statement) {
            return this.statement.execute(statement);
        }
    }

    public ResultSet executeQuery(String query) throws SQLException {
        synchronized (statement) {
            return statement.executeQuery(query);
        }
    }

    public PreparedStatement prepareStatement(String sql) throws SQLException {
        return connection.prepareStatement(sql);
    }

    @Override
    public void close() throws SQLException {
        statement.close();
        connection.close();
    }
}
