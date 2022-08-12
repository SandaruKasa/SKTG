use teloxide::{prelude::*, types::Message, utils::command::BotCommands};

use crate::types::*;

#[derive(BotCommands, Clone)]
#[command(rename = "lowercase", description = "")]
pub enum MiscCommands {
    #[command(description = "off")]
    Shrug,
    #[command(description = "off")]
    GitHub,
    #[command(description = "off")]
    Source,
}

use MiscCommands::*;

pub async fn misc(bot: TelegramBot, message: Message, command: MiscCommands) -> Res<()> {
    bot.send_message(
        message.chat.id,
        match command {
            Shrug => "¯\\_(ツ)_/¯",
            GitHub | Source => "https://github.com/SandaruKasa/SKTG/tree/rust",
        },
    )
    .reply_to_message_id(message.id)
    .disable_web_page_preview(true)
    .await?;
    Ok(())
}
