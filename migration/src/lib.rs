pub use sea_orm_migration::prelude::*;

mod create_admins_table;

pub(crate) async fn execute_sqls(
    manager: &SchemaManager<'_>,
    sqls: impl IntoIterator<Item = impl ToString>,
) -> Result<(), DbErr> {
    use sea_orm::{ConnectionTrait, Statement};

    let backend = manager.get_database_backend();
    let connection = manager.get_connection();
    for sql in sqls {
        connection
            .execute(Statement::from_string(backend, sql.to_string()))
            .await?;
    }
    Ok(())
}

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![Box::new(create_admins_table::Migration)]
    }
}
