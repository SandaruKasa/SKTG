package sandarukasa.SKTG;

import net.bramp.ffmpeg.FFmpegExecutor;
import net.bramp.ffmpeg.builder.FFmpegBuilder;
import org.telegram.telegrambots.TelegramBotsApi;
import org.telegram.telegrambots.api.methods.send.SendAudio;
import org.telegram.telegrambots.api.methods.send.SendMessage;
import org.telegram.telegrambots.api.objects.Message;
import org.telegram.telegrambots.api.objects.Voice;
import org.telegram.telegrambots.exceptions.TelegramApiException;

import java.io.File;
import java.io.IOException;
import java.util.ResourceBundle;

public class BetaLupi extends AbstractTelegramBot {
    private static final FFmpegExecutor fFmpegExecutor;

    static {
        try {
            fFmpegExecutor = new FFmpegExecutor();
        } catch (IOException e) {
            throw new RuntimeException("Failed to initialize FFMPEG executor");
        }
    }

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
    protected final void oggToMp3(Message message) throws TelegramApiException {
        Voice voice = message.getVoice();
        if (voice == null) {
            final Message replied = message.getReplyToMessage();
            if (replied != null) {
                voice = replied.getVoice();
            }
        }
        if (voice == null) {
            replyWithAMessage(message, new SendMessage().setText("No audio"));
        } else {
            final String oggAbsPath = downloadFileById(voice.getFileId()).getAbsolutePath();
            final String mp3AbsPath = String.format("%s.mp3", oggAbsPath);
            fFmpegExecutor.createJob(new FFmpegBuilder().addInput(oggAbsPath).addOutput(mp3AbsPath).setFormat("mp3").done()).run();
            replyWithAnAudio(message, new SendAudio().setNewAudio(new File(oggAbsPath)));
        }
    }
}
