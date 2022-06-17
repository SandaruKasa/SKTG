use anyhow::{Context as _, Result};
use teloxide::{dispatching::UpdateFilterExt, prelude::*};

mod config;
mod features;
mod persistance;
mod types;

use features::*;

#[tokio::main]
async fn main() -> Result<()> {
    config::init_logging();
    log::info!("Initializing persistance...");
    persistance::init()
        .await
        .context("Error initializing persistance")?;
    log::info!("Initializing bot...");
    let bot = Bot::new(config::get_token()?).auto_send();
    log::info!("Starting {}...", bot.get_me().await.unwrap().username());
    log::info!("Setting up commands...");
    bot.set_my_commands(get_commands())
        .await
        .context("Error setting up comamnds")?;
    log::info!("Commands are set up");
    let handler = Update::filter_message()
        .branch(
            dptree::entry()
                .filter_command::<MiscCommands>()
                .endpoint(misc),
        )
        .chain(
            dptree::entry()
                .filter_command::<InspirobotCommands>()
                .endpoint(inspirobot),
        );
    Dispatcher::builder(bot, handler)
        .error_handler(LoggingErrorHandler::new())
        .default_handler(move |_update| async {})
        .build()
        .setup_ctrlc_handler()
        .dispatch()
        .await;
    Ok(())
}
