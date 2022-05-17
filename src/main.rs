use std::env;

use anyhow::Result;
use teloxide::{dispatching::UpdateFilterExt, prelude::*};

mod config;
mod features;
mod types;

use features::*;

#[tokio::main]
async fn main() -> Result<()> {
    if env::var("RUST_LOG").is_err() {
        env::set_var("RUST_LOG", "INFO")
    }
    pretty_env_logger::init();
    log::info!("Initializing bot...");
    let bot = Bot::new(config::get_token()?).auto_send();
    log::info!("Starting {}...", bot.get_me().await.unwrap().username());

    let handler = Update::filter_message().branch(
        dptree::entry()
            .filter_command::<InspirobotCommands>()
            .endpoint(inspirobot),
    );
    Dispatcher::builder(bot, handler)
        .error_handler(LoggingErrorHandler::new())
        .build()
        .setup_ctrlc_handler()
        .dispatch()
        .await;
    Ok(())
}
