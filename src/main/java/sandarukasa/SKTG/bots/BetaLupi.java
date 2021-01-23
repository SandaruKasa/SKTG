package sandarukasa.SKTG.bots;

import net.bramp.ffmpeg.FFmpegExecutor;
import net.bramp.ffmpeg.builder.FFmpegBuilder;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.api.methods.ActionType;
import org.telegram.telegrambots.meta.api.methods.send.SendAudio;
import org.telegram.telegrambots.meta.api.methods.send.SendPhoto;
import org.telegram.telegrambots.meta.api.objects.*;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import sandarukasa.SKTG.bots.betalupi.InspirobotMe;
import sandarukasa.SKTG.bots.handler_annotations.CommandHandler;
import sandarukasa.SKTG.bots.handler_annotations.TextTriggerHandler;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
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

    @CommandHandler(commandName = "shrug", commandAliases = {}, availableInTheList = true,
            description = "Sends a ¯\\_(ツ)_/¯")
    protected final void shrug(Message message) throws TelegramApiException {
        replyWithLocalizedText(message, "shrug");
    }


    @CommandHandler(commandName = "jpeg", commandAliases = {"jpg", "compress"}, availableInTheList = true,
            description = "Compresses a photo")
    protected final void jpeg(Message message) throws TelegramApiException {
        List<PhotoSize> photo = message.getPhoto();
        if (photo == null) {
            final Message replied = message.getReplyToMessage();
            if (replied != null) {
                photo = replied.getPhoto();
            }
        }
        if (photo == null) {
            replyWithLocalizedText(message, "no_photo");
        } else {
            //todo
        }
    }


    @CommandHandler(commandName = "inspire", commandAliases = {}, availableInTheList = true,
            description = "Sends an AI-generated inspirational picture")
    protected final void inspire(Message message) throws TelegramApiException, IOException, InterruptedException {
        sendChatAction(message.getChatId(), ActionType.UPLOADPHOTO);
        final InspirobotMe.Picture picture = InspirobotMe.getPicture();
        replyWithPhoto(message, SendPhoto.builder().photo(new InputFile(picture.getUrl())).caption(picture.getSharePageUrl()));

    }

    @CommandHandler(commandName = "mp3", commandAliases = {}, availableInTheList = true,
            description = "Converts a voice message to mp3")
    protected final void oggToMp3(Message message) throws TelegramApiException, IOException {
        Voice voice = message.getVoice();
        if (voice == null) {
            final Message replied = message.getReplyToMessage();
            if (replied != null) {
                voice = replied.getVoice();
            }
        }
        if (voice == null) {
            replyWithLocalizedText(message, "no_audio");
        } else {
            sendChatAction(message.getChatId(), ActionType.UPLOADAUDIO);
            final Path ogg = getFile(voice.getFileId());
            final Path mp3 = Path.of(ogg + ".mp3");
            synchronized (fFmpegExecutor) {
                fFmpegExecutor.createJob(new FFmpegBuilder().addInput(ogg.toString()).addOutput(mp3.toString())
                        .setFormat("mp3").done()).run();
            }
            replyWithAudio(message, SendAudio.builder().audio(new InputFile(mp3.toFile())));
            deleteFiles(ogg, mp3);
        }
    }

    @TextTriggerHandler(regex = "(?Ui).*слава укра(їні|ине).*")
    protected final void gloryToHeroes(Message message) throws TelegramApiException {
        replyWithText(message, "Героям Слава!");
    }


    @Override
    public void onCallbackQueryReceived(CallbackQuery callbackQuery) {
        // todo
        super.onCallbackQueryReceived(callbackQuery);
    }
}
