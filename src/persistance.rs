use anyhow::{Context as _, Result};
use migration::{Migrator, MigratorTrait};
use sea_orm::{ConnectOptions, Database, DatabaseConnection};

pub mod entity;

use crate::config::SQLITE_FILE_PATH;

pub async fn connect() -> Result<DatabaseConnection> {
    let mut options = ConnectOptions::new(format!("sqlite://{}", &*SQLITE_FILE_PATH));
    // todo: change to `sqlx_logging_level` when PR accepted
    options.sqlx_logging(log::max_level() >= log::LevelFilter::Debug);
    Database::connect(options)
        .await
        .context("Error connecting to database")
}

pub async fn init() -> Result<()> {
    log::info!("Applying migrations...");
    let connection = connect().await?;
    Migrator::up(&connection, None)
        .await
        .context("Error applying migrations")
}
