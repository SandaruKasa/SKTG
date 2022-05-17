use std::env;

use teloxide::{prelude::*, utils::command::BotCommands};

mod features;
mod types;

fn get_token() -> String {
    use std::{
        fs::File,
        io::{BufRead, BufReader},
    };

    if let Ok(token) = env::var("TELOXIDE_TOKEN").or(env::var("BOT_TOKEN")) {
        return token;
    }

    log::debug!("No env variable with token found, defaulting to reading from file...");

    let token_file_path = match env::var("BOT_TOKEN_FILE") {
        Ok(path) => path,
        Err(_) => {
            log::debug!("BOT_TOKEN_FILE env variable not set, defaulting to `token.txt`...");
            "token.txt".to_string()
        }
    };

    File::open(&token_file_path)
        .and_then(|file| {
            let mut token = String::new();
            BufReader::new(file).read_line(&mut token).map(|_| token)
        })
        .map_err(|err| {
            format!(
                "Error reading token from file {:?}:\n{:?}",
                token_file_path, err
            )
        })
        .unwrap()
}

#[tokio::main]
async fn main() {
    if env::var("RUST_LOG").is_err() {
        env::set_var("RUST_LOG", "INFO")
    }
    pretty_env_logger::init();
    log::info!("Initializing bot...");
    let bot = Bot::new(get_token()).auto_send();
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
