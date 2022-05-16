use reqwest::Url;
use teloxide::{
    payloads::SendPhotoSetters, prelude::*, types::InputFile, utils::command::BotCommands,
};

use std::error::Error;

#[tokio::main]
async fn main() {
    pretty_env_logger::init();
    log::info!("Initializing bot...");
    let bot = Bot::from_env().auto_send();
    log::info!("Starting {}...", bot.get_me().await.unwrap().username());
    teloxide::commands_repl(bot, answer, Command::ty()).await;
}

//todo: set_my_commands
#[derive(BotCommands, Clone)]
#[command(rename = "lowercase", description = "These commands are supported:")]
enum Command {
    #[command(description = "display this text.")]
    Help,
    #[command(description = "send an AI-generated inspirational quote.")]
    Inspire,
}

async fn answer(
    bot: AutoSend<Bot>,
    message: Message,
    command: Command,
) -> Result<(), Box<dyn Error + Send + Sync>> {
    match command {
        Command::Help => {
            bot.send_message(message.chat.id, Command::descriptions().to_string())
                .await?;
        }
        // todo: Christmas
        // todo: modules
        Command::Inspire => {
            bot.send_chat_action(message.chat.id, teloxide::types::ChatAction::UploadPhoto)
                .await
                .ok();
            let picture_url = reqwest::get("https://inspirobot.me/api?generate=true")
                .await?
                .text()
                .await?;
            let picture_url = Url::parse(&picture_url)?;
            bot.send_photo(message.chat.id, InputFile::url(picture_url.clone()))
                .reply_to_message_id(message.id)
                .caption(format!(
                    "https://inspirobot.me/share?iuid={}",
                    picture_url.path().trim_start_matches("/")
                ))
                .await?;
        }
    };

    Ok(())
}
