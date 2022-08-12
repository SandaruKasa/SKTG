use anyhow::{Context as _, Result};
use lazy_static::LazyStatic;
use sea_orm::EntityTrait;
use teloxide::dispatching::UpdateFilterExt;

mod config;
mod features;
mod persistance;
mod types;

use features::*;
use types::*;

async fn message_admins(bot: &TelegramBot, text: impl ToString) -> Result<()> {
    use persistance::entity::prelude::*;
    let text = text.to_string();
    let db = &persistance::connect().await?;
    for admin in BotAdmin::find()
        .all(db)
        .await
        .context("Error getting admins")?
    {
        if let Err(e) = bot.send_message(UserId(admin.user_id as u64), &text).await {
            log::error!(
                "Error sending {:?} to admin {}: {:?}",
                text,
                admin.user_id,
                e
            );
        }
    }
    Ok(())
}

async fn init() -> Result<TelegramBot> {
    config::init_logging();

    log::info!("Initializing persistance...");
    persistance::init()
        .await
        .context("Error initializing persistance")?;
    log::info!("Persistance initialized");

    log::info!("Initializing bot...");
    let bot = Bot::new(config::get_token()?).auto_send();

    // TODO: username support
    config::init_admins().await?;

    log::info!("Setting up commands...");
    bot.set_my_commands(get_commands())
        .await
        .context("Error setting up commands")?;
    log::info!("Commands are set up");

    let me = bot.get_me().await.context("Error getting bot info")?;
    LazyStatic::initialize(&config::STARTUP_TIME);

    log::info!("Bot @{} initialized", me.username());
    Ok(bot)
}

#[tokio::main]
async fn main() -> Result<()> {
    let bot = init().await?;

    message_admins(&bot, "Hello!")
        .await
        .context("Error greeting admins")?;

    let handler = Update::filter_message()
        .branch(
            dptree::entry()
                .filter_command::<MiscCommands>()
                .endpoint(misc),
        )
        .branch(
            dptree::entry()
                .filter_command::<InspirobotCommands>()
                .endpoint(inspirobot),
        )
        .branch(
            dptree::entry()
                .filter_command::<AdminCommands>()
                .endpoint(admin),
        );
    log::info!("Starting the dispatcher");
    Dispatcher::builder(bot, handler)
        .error_handler(LoggingErrorHandler::new())
        .default_handler(move |_update| async {})
        .enable_ctrlc_handler()
        .build()
        .dispatch()
        .await;
    Ok(())
}
