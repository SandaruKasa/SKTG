use sea_orm_migration::prelude::*;

pub struct Migration;

impl MigrationName for Migration {
    fn name(&self) -> &str {
        "Example migartion"
    }
}

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        dbg!("Up...", manager.get_connection());
        Ok(()) //todo:
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        dbg!("Down...", manager.get_connection());
        Ok(()) //todo
    }
}
