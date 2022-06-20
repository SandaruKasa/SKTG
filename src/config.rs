use std::{
    env,
    ffi::{OsStr, OsString},
    fs::{read_to_string, File},
    io::{BufRead, BufReader},
    path::{Path, PathBuf},
    time,
};

use anyhow::{Context, Result};
use env_logger::{self, Builder, Env};
use lazy_static::lazy_static;
use sea_orm::prelude::*;
use teloxide::types::UserId;

use crate::persistance::{self, entity::bot_admin};

pub fn get_env_var_or_default(key: impl AsRef<OsStr>, default: impl Into<OsString>) -> OsString {
    let key = key.as_ref();
    let default = default.into();
    if let Some(result) = env::var_os(key) {
        result
    } else {
        log::info!("{key:?} not set, defaulting to {default:?}");
        default
    }
}

pub fn init_logging() {
    Builder::from_env(Env::default().default_filter_or("INFO")).init()
}

const DATABASE_FILE: &str = "DATABASE_FILE";
lazy_static! {
    pub static ref SQLITE_FILE_PATH: String = get_env_var_or_default(DATABASE_FILE, "sktg.sqlite3")
        .into_string()
        .unwrap_or_else(|_| panic!(
            "Due to sea-orm limitations, {:?} must be valid Unicode",
            DATABASE_FILE
        ));
}

pub fn get_token() -> Result<String> {
    if let Ok(token) = std::env::var("BOT_TOKEN") {
        return Ok(token);
    }
    log::debug!("No env variable with token found, defaulting to reading from file...");
    let token_file_path = get_env_var_or_default("BOT_TOKEN_FILE", "token.txt");
    read_to_string(&token_file_path)
        .with_context(|| format!("Error reading token from {:?}", token_file_path))
        .map(|line| line.trim().to_owned())
}

fn read_admins(path: impl AsRef<Path>) -> Result<Vec<UserId>> {
    let mut result = vec![];
    let file = BufReader::new(File::open(&path).context("Error opening file")?);
    for line in file.lines() {
        let line = line.context("Error reading from file")?;
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        result.push(UserId(
            line.parse()
                .with_context(|| format!("Error parsing user_id {line:?}"))?,
        ))
    }
    Ok(result)
}

pub async fn is_admin(db: &DatabaseConnection, user_id: UserId) -> Result<bool> {
    bot_admin::Entity::find()
        .filter(bot_admin::Column::UserId.eq(user_id.0 as i64))
        .one(db)
        .await
        .with_context(|| format!("Error checking whether {user_id:?} is an admin"))
        .map(|option| option.is_some())
}

pub async fn add_admin(
    db: &DatabaseConnection,
    user_id: UserId,
) -> Result<Option<bot_admin::Model>> {
    if is_admin(db, user_id).await? {
        Ok(None)
    } else {
        bot_admin::ActiveModel {
            user_id: sea_orm::Set(user_id.0 as i64),
            ..Default::default()
        }
        .insert(db)
        .await
        .with_context(|| format!("Error adding admin {user_id:?}"))
        .map(Some)
    }
}

pub async fn init_admins() -> Result<()> {
    let path: PathBuf = get_env_var_or_default("BOT_ADMINS_FILE", "admins.txt").into();
    if path.exists() {
        log::info!("Initializing admins");
        let admins =
            read_admins(&path).with_context(|| format!("Error reading admins from {path:?}"))?;
        if admins.is_empty() {
            log::warn!("No admins found in {path:?}")
        } else {
            let db = &persistance::connect().await?;
            for user_id in admins {
                match add_admin(db, user_id).await? {
                    Some(admin) => log::info!("Admin {admin:?} added"),
                    None => log::info!("Admin {user_id:?} already added"),
                }
            }
            log::info!("Admins initialized");
        }
    } else {
        log::info!("{path:?} doesn't exist, so not initializing admins")
    }
    Ok(())
}

lazy_static! {
    pub static ref STARTUP_TIME: time::Instant = time::Instant::now();
}

/// Rounds to whole seconds
pub fn get_uptime() -> time::Duration {
    time::Duration::from_secs(STARTUP_TIME.elapsed().as_secs())
}
