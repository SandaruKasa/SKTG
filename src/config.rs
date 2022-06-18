use std::{
    env,
    fs::File,
    io::{BufRead, BufReader},
};

use anyhow::{Context, Result};
use env_logger::{self, Builder, Env};
use lazy_static::lazy_static;

pub fn init_logging() {
    Builder::from_env(Env::default().default_filter_or("INFO")).init()
}

fn get_from_env_or_default(key: impl AsRef<std::ffi::OsStr>, default: &'static str) -> String {
    let key = key.as_ref();
    env::var(key).unwrap_or_else(|err| {
        use env::VarError::*;
        match err {
            NotPresent => {
                log::info!("{:?} not set, defaulting to {:?}", key, default)
            }
            NotUnicode(var) => panic!(
                "Error getting {:?} env variable: it is not unicode: {:?}",
                key, var
            ),
        }
        default.to_string()
    })
}

lazy_static! {
    pub static ref SQLITE_FILE_PATH: String =
        get_from_env_or_default("DATABASE_FILE", "sktg.sqlite3");
}

fn read_token(token_file_path: &str) -> Result<String> {
    let file = File::open(token_file_path).context("Error opening file")?;
    let mut token = String::new();
    BufReader::new(file)
        .read_line(&mut token)
        .context("Error reading form file")?;
    Ok(token)
}

pub fn get_token() -> Result<String> {
    if let Ok(token) = env::var("TELOXIDE_TOKEN").or_else(|_| env::var("BOT_TOKEN")) {
        return Ok(token);
    }
    log::debug!("No env variable with token found, defaulting to reading from file...");
    let token_file_path = get_from_env_or_default("BOT_TOKEN_FILE", "token.txt");
    read_token(&token_file_path)
        .with_context(|| format!("Error reading token from file {:?}", token_file_path))
}
