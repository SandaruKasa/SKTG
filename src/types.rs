pub use teloxide::prelude::*;
pub type Res<T> = std::result::Result<T, Box<dyn std::error::Error + Send + Sync>>;
pub type TelegramBot = AutoSend<Bot>;
