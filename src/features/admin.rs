use teloxide::{prelude::*, types::Message, utils::command::BotCommands};

use crate::{config, persistance, types::*};

#[derive(BotCommands, Clone)]
#[command(rename = "lowercase", description = "")]
pub enum AdminCommands {
    #[command(description = "off")]
    Uptime,
}

use AdminCommands::*;

pub async fn admin(bot: TelegramBot, message: Message, command: AdminCommands) -> Res<()> {
    let user_id = message
        .from()
        .ok_or_else(|| format!("Message without a sender: {message:?}"))?
        .id;
    let db = &persistance::connect().await?;
    if config::is_admin(db, user_id).await? {
        match command {
            Uptime => {
                bot.send_message(
                    message.chat.id,
                    humantime::format_duration(config::get_uptime()).to_string(),
                )
                .reply_to_message_id(message.id)
                .await?;
            }
        }
    } else {
        bot.send_message(message.chat.id, "You are not an admin")
            .reply_to_message_id(message.id)
            .await?;
    }
    Ok(())
}
