use std::{
    env,
    fs::File,
    io::{BufRead, BufReader},
};

use anyhow::{Context, Result};
use env_logger::{self, Builder, Env};

pub fn init_logging() {
    Builder::from_env(Env::default().default_filter_or("INFO")).init()
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
    if let Ok(token) = env::var("TELOXIDE_TOKEN").or(env::var("BOT_TOKEN")) {
        return Ok(token);
    }

    log::debug!("No env variable with token found, defaulting to reading from file...");

    let token_file_path = match env::var("BOT_TOKEN_FILE") {
        Ok(path) => path,
        Err(_) => {
            log::debug!("BOT_TOKEN_FILE env variable not set, defaulting to `token.txt`...");
            "token.txt".to_string()
        }
    };
    read_token(&token_file_path)
        .with_context(|| format!("Error reading token from file {:?}", token_file_path))
}
