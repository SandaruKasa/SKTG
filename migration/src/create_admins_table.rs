use sea_orm_migration::prelude::*;

pub struct Migration;

impl MigrationName for Migration {
    fn name(&self) -> &str {
        "Create admins table"
    }
}

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        crate::execute_sqls(
            manager,
            [
                r#"
                CREATE TABLE `BotAdmin` (
                    `id` integer NOT NULL PRIMARY KEY,
                    `user_id` integer NOT NULL UNIQUE
                )"#,
                "CREATE UNIQUE INDEX `BotAdmin_user_id` ON `BotAdmin` (`user_id`)",
            ],
        )
        .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        crate::execute_sqls(manager, ["DROP TABLE `BotAdmin`"]).await
    }
}
