package sandarukasa.SKTG.bots;

import net.bramp.ffmpeg.FFmpegExecutor;
import net.bramp.ffmpeg.builder.FFmpegBuilder;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.api.methods.ActionType;
import org.telegram.telegrambots.meta.api.methods.send.SendAudio;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.methods.send.SendPhoto;
import org.telegram.telegrambots.meta.api.objects.InputFile;
import org.telegram.telegrambots.meta.api.objects.Message;
import org.telegram.telegrambots.meta.api.objects.PhotoSize;
import org.telegram.telegrambots.meta.api.objects.Voice;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import sandarukasa.SKTG.bots.handler_annotations.CommandHandler;
import sandarukasa.SKTG.bots.handler_annotations.TextTriggerHandler;
import sandarukasa.SKTG.misc.InspirobotMe;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;
import javax.imageio.stream.ImageOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
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

    public static File getCompressedPhoto(File uncompressed, float compressionQuality) throws IOException {
        // https://stackoverflow.com/a/44566972
        File compressed = new File(String.format("%s.jpg", uncompressed.getAbsolutePath()));
        OutputStream outputStream = new FileOutputStream(compressed);
        ImageWriter imageWriter = ImageIO.getImageWritersByFormatName("jpg").next();
        ImageOutputStream imageOutputStream = ImageIO.createImageOutputStream(outputStream);
        imageWriter.setOutput(imageOutputStream);
        ImageWriteParam param = imageWriter.getDefaultWriteParam();
        param.setCompressionMode(ImageWriteParam.MODE_EXPLICIT);
        param.setCompressionQuality(compressionQuality);
        imageWriter.write(null, new IIOImage(ImageIO.read(uncompressed), null, null), param);
        outputStream.close();
        imageOutputStream.close();
        imageWriter.dispose();
        return compressed;
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
    protected final void jpeg(Message message) throws IOException, TelegramApiException {
        List<PhotoSize> photo = message.getPhoto();
        if (photo == null) {
            final Message replied = message.getReplyToMessage();
            if (replied != null) {
                photo = replied.getPhoto();
            }
        }
        if (photo == null) {
            replyWithMessage(message, SendMessage.builder().text(getString("no_photo", message.getFrom())));
        } else {
            float compressionQuality;
            try {
                compressionQuality = switch (Integer.parseInt(message.getText().split("(?U)\\s+")[1])) {
                    case 1 -> 0.2f;
                    default -> 0.1f;
                    case 3 -> 0.05f;
                    case 4 -> 0f;
                };
            } catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
                compressionQuality = 0.1f;
            }
            // todo buttons
            replyWithPhoto(message, SendPhoto.builder().photo(
                    new InputFile(getCompressedPhoto(downloadFileById(photo.get(photo.size() - 1).getFileId())
                            , compressionQuality))));
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
    protected final void oggToMp3(Message message) throws TelegramApiException {
        sendChatAction(message.getChatId(), ActionType.UPLOADAUDIO);
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
            final String oggAbsPath = downloadFileById(voice.getFileId()).getAbsolutePath();
            final String mp3AbsPath = String.format("%s.mp3", oggAbsPath);
            fFmpegExecutor.createJob(new FFmpegBuilder().addInput(oggAbsPath).addOutput(mp3AbsPath).setFormat("mp3").done()).run();
            replyWithAudio(message, SendAudio.builder().audio(new InputFile(new File(oggAbsPath))));
        }
    }

    @TextTriggerHandler(regex = "(?Ui).*слава укра(їні|ине).*")
    protected final void gloryToHeroes(Message message) throws TelegramApiException {
        replyWithText(message, "Героям Слава!");
    }
}
