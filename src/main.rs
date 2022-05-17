use teloxide::{prelude::*, utils::command::BotCommands};

mod features;
mod types;

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

async fn answer(bot: AutoSend<Bot>, message: Message, command: Command) -> types::Result<()> {
    use features::*;
    match command {
        Command::Help => {
            bot.send_message(message.chat.id, Command::descriptions().to_string())
                .await?;
        }
        Command::Inspire => inspirobot(bot, message).await?,
    };

    Ok(())
}
