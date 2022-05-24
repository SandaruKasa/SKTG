use teloxide::{adaptors::AutoSend, prelude::*, types::Message, utils::command::BotCommands, Bot};

use crate::types::Res;

#[derive(BotCommands, Clone)]
#[command(rename = "lowercase", description = "")]
pub enum MiscCommands {
    #[command()]
    Shrug,
    #[command()]
    GitHub,
    #[command()]
    Source,
}

use MiscCommands::*;

pub async fn misc(bot: AutoSend<Bot>, message: Message, command: MiscCommands) -> Res<()> {
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
