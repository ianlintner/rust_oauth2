use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub jwt: JwtConfig,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct JwtConfig {
    pub secret: String,
}

impl Default for Config {
    fn default() -> Self {
        // Require JWT secret to be explicitly set via environment variable
        let jwt_secret = std::env::var("OAUTH2_JWT_SECRET")
            .expect("OAUTH2_JWT_SECRET environment variable must be set. Generate a secure random string (minimum 32 characters).");
        
        Self {
            server: ServerConfig {
                host: std::env::var("OAUTH2_SERVER_HOST").unwrap_or_else(|_| "127.0.0.1".to_string()),
                port: std::env::var("OAUTH2_SERVER_PORT")
                    .ok()
                    .and_then(|p| p.parse().ok())
                    .unwrap_or(8080),
            },
            database: DatabaseConfig {
                url: std::env::var("OAUTH2_DATABASE_URL").unwrap_or_else(|_| "sqlite:oauth2.db".to_string()),
            },
            jwt: JwtConfig {
                secret: jwt_secret,
            },
        }
    }
}

impl Config {
    pub fn from_env() -> Result<Self, config::ConfigError> {
        let config = config::Config::builder()
            .add_source(config::Environment::with_prefix("OAUTH2"))
            .build()?;
        
        config.try_deserialize()
    }
}
