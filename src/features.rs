mod admin;
mod inspirobot;
mod misc;

pub use admin::*;
pub use inspirobot::*;
pub use misc::*;
use teloxide::{types::BotCommand, utils::command::BotCommands};

pub fn get_commands() -> impl Iterator<Item = BotCommand> {
    [
        MiscCommands::bot_commands(),
        InspirobotCommands::bot_commands(),
    ]
    .into_iter()
    .flatten()
}
