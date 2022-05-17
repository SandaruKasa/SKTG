pub type Res<T> = std::result::Result<T, Box<dyn std::error::Error + Send + Sync>>;
