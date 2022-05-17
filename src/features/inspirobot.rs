use chrono::{Datelike, Utc};
use reqwest::Url;
use teloxide::{
    adaptors::AutoSend,
    prelude::*,
    types::{InputFile, Message},
    Bot,
};

use crate::types::Result;

pub async fn inspirobot(bot: AutoSend<Bot>, message: Message) -> Result<()> {
    bot.send_chat_action(message.chat.id, teloxide::types::ChatAction::UploadPhoto)
        .await
        .ok();

    let today = Utc::now();
    let website =
        if today.month() == 12 && today.day() >= 20 || today.month() == 1 && today.day() <= 14 {
            "xmascardbot.com"
        } else {
            "inspirobot.me"
        };
    let api_url = format!("https://{}/api?generate=true", website);
    let picture_url = Url::parse(&reqwest::get(&api_url).await?.text().await?)?;
    bot.send_photo(message.chat.id, InputFile::url(picture_url.clone()))
        .reply_to_message_id(message.id)
        .caption(format!(
            "https://{}/share?iuid={}",
            website,
            picture_url.path().trim_start_matches("/")
        ))
        .await?;
    Ok(())
}
