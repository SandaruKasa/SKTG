package sandarukasa.SKTG.misc;


import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Calendar;

public class InspirobotMe {
    protected static final HttpClient httpClient = HttpClient.newHttpClient();


    protected static boolean isChristmasSeason() {
        Calendar currentDate = Calendar.getInstance();
        var currentMonth = currentDate.get(Calendar.MONTH);
        var currentDay = currentDate.get(Calendar.DAY_OF_MONTH);
        return currentMonth == Calendar.DECEMBER && currentDay > 22 ||
                currentMonth == Calendar.JANUARY && currentDay < 9;
    }

    public static Picture getPicture(boolean christmas) throws IOException, InterruptedException {
        final String site = christmas ? "xmascardbot.com" : "inspirobot.me";
        final String pictureUrl = httpClient.send(
                HttpRequest.newBuilder(URI.create(String.format("https://www.%s/api?generate=true", site))).build(),
                HttpResponse.BodyHandlers.ofString()
        ).body();
        return new Picture(pictureUrl,
                String.format("https://%s/share?iuid=%s", site, new URL(pictureUrl).getPath().substring(1)));
    }

    public static Picture getPicture() throws IOException, InterruptedException {
        return getPicture(isChristmasSeason());
    }

    public static final class Picture {
        private final String url;
        private final String sharingUrl;

        public Picture(String url, String sharingUrl) {
            this.url = url;
            this.sharingUrl = sharingUrl;
        }

        public String getUrl() {
            return url;
        }

        public String getSharePageUrl() {
            return sharingUrl;
        }
    }
}
