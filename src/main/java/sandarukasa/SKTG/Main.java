package sandarukasa.SKTG;

import com.vk.api.sdk.client.VkApiClient;
import com.vk.api.sdk.client.actors.UserActor;
import com.vk.api.sdk.httpclient.HttpTransportClient;
import net.bramp.ffmpeg.FFmpegExecutor;
import net.bramp.ffmpeg.builder.FFmpegBuilder;
import org.telegram.telegrambots.exceptions.TelegramApiException;

import java.io.IOException;
import java.util.ResourceBundle;

public class Main {
    private static final ResourceBundle TOKENS = ResourceBundle.getBundle("tokens");

    private static String getToken(String key) {
        return TOKENS.getString(key);
    }

    public static void main(String[] args) throws TelegramApiException, IOException {
        org.telegram.telegrambots.ApiContextInitializer.init();
        VkApiClient vkApiClient = new VkApiClient(HttpTransportClient.getInstance());
        UserActor userActor = new UserActor(Integer.parseInt(getToken("vk_actor_id")), getToken("vk_token"));
//        GetResponse b = null;
//        try {
//            b = vkApiClient.wall().get(userActor).ownerId(1).count(1).execute();
//        } catch (ApiException | ClientException e) {
//            e.printStackTrace();
//        }
//        final TestBot testBot = new TestBot(new TelegramBotsApi(), TOKENS);

        new FFmpegExecutor().createJob(new FFmpegBuilder().addInput("1.ogg").addOutput("1.mp3").setFormat("mp3").done()).run();

    }
}
