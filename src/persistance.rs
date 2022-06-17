use std::fs::OpenOptions;

use anyhow::{Context as _, Result};
use migration::{Migrator, MigratorTrait};
use sea_orm::{ConnectOptions, Database, DatabaseConnection, DbErr};

const SQLITE_FILE_PATH: &str = "sktg.sqlite3";

pub async fn connect() -> Result<DatabaseConnection, DbErr> {
    let mut options = ConnectOptions::new(format!("sqlite://{}", SQLITE_FILE_PATH));
    // todo: change to `sqlx_logging_level` when PR accepted
    options.sqlx_logging(log::max_level() >= log::LevelFilter::Debug);
    Database::connect(options).await
}

async fn apply_migrations() -> Result<(), DbErr> {
    log::info!("Applying migrations...");
    let connection = connect().await?;
    Migrator::up(&connection, None).await
}

pub async fn init() -> Result<()> {
    OpenOptions::new()
        .create(true)
        .append(true)
        .open(SQLITE_FILE_PATH)
        .with_context(|| {
            format!(
                "Error making sure that the database file {:?} exists",
                SQLITE_FILE_PATH
            )
        })?;
    apply_migrations()
        .await
        .context("Error applying migartions")?;
    Ok(())
}
