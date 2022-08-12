use chrono::{Datelike, Utc};
use reqwest::Url;
use teloxide::{
    prelude::*,
    types::{InputFile, Message},
    utils::command::BotCommands,
};

use crate::types::*;

#[derive(BotCommands, Clone)]
#[command(rename = "lowercase", description = "")]
pub enum InspirobotCommands {
    #[command(description = "send an AI-generated inspirational-quote")]
    Inspire,
    #[command(description = "off")]
    Inspirobot,
    #[command(description = "off")]
    Xmas,
}

use InspirobotCommands::*;

fn is_christmas() -> bool {
    let today = Utc::now();
    today.month() == 12 && today.day() >= 20 || today.month() == 1 && today.day() <= 14
}

const XMASCARDBOT: &str = "xmascardbot.com";
const INSPIROBOT: &str = "inspirobot.me";

pub async fn inspirobot(
    bot: TelegramBot,
    message: Message,
    command: InspirobotCommands,
) -> Res<()> {
    bot.send_chat_action(message.chat.id, teloxide::types::ChatAction::UploadPhoto)
        .await
        .ok();

    let website = match command {
        Inspire => {
            if is_christmas() {
                XMASCARDBOT
            } else {
                INSPIROBOT
            }
        }
        Xmas => XMASCARDBOT,
        Inspirobot => INSPIROBOT,
    };

    let api_url = format!("https://{}/api?generate=true", website);
    let picture_url = Url::parse(&reqwest::get(&api_url).await?.text().await?)?;
    bot.send_photo(message.chat.id, InputFile::url(picture_url.clone()))
        .reply_to_message_id(message.id)
        .caption(format!(
            "https://{}/share?iuid={}",
            website,
            picture_url.path().trim_start_matches('/')
        ))
        .await?;
    Ok(())
}
