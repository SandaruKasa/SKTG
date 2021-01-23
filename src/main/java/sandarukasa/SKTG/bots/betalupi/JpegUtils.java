package sandarukasa.SKTG.bots.betalupi;

import org.telegram.telegrambots.meta.api.objects.PhotoSize;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;
import javax.imageio.stream.ImageOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;


public class JpegUtils {
    public static int photoSizeToNumberOfPixels(PhotoSize photoSize) {
        return photoSize.getWidth() * photoSize.getHeight();
    }

    public static float compressionLevelToCompressionQuality(int compressionLevel) {
        return switch (compressionLevel) {
            case 0 -> 1.00f;
            case 1 -> 0.20f;
            default -> 0.10f;
            case 3 -> 0.05f;
            case 4 -> 0.00f;
        };
    }

    public static java.io.File compress(java.io.File uncompressed, float compressionQuality)
            throws IOException {
        // https://stackoverflow.com/a/44566972
        java.io.File compressed = new java.io.File(String.format("%s.jpg", uncompressed.getAbsolutePath()));
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
}
