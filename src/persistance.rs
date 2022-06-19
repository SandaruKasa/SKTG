use anyhow::{Context as _, Result};
use migration::{Migrator, MigratorTrait};
use sea_orm::{ConnectOptions, Database, DatabaseConnection, DbErr};

use crate::config::SQLITE_FILE_PATH;

pub async fn connect() -> Result<DatabaseConnection, DbErr> {
    let mut options = ConnectOptions::new(format!("sqlite://{}", &*SQLITE_FILE_PATH));
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
    apply_migrations()
        .await
        .context("Error applying migrations")?;
    Ok(())
}
