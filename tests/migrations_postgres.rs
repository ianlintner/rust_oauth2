use sqlx::{postgres::PgPoolOptions, Executor};
use std::{fs, path::PathBuf, time::Duration};
use testcontainers::clients::Cli;
use testcontainers_modules::postgres::Postgres as TcPostgres;

// This test spins up a disposable Postgres via Testcontainers, applies our SQLx migrations,
// and verifies the schema is valid. Skips automatically unless RUN_TESTCONTAINERS=1 is set
// to avoid breaking environments without Docker (e.g., CI without privileges).
#[tokio::test]
async fn migrations_apply_successfully_on_postgres() -> Result<(), Box<dyn std::error::Error>> {
    if std::env::var("RUN_TESTCONTAINERS").as_deref() != Ok("1") {
        eprintln!("skipping migrations_postgres test (set RUN_TESTCONTAINERS=1 to run)");
        return Ok(());
    }

    let docker = Cli::default();
    let node = docker.run(TcPostgres::default());
    let port = node.get_host_port_ipv4(5432);
    let url = format!("postgres://postgres:postgres@127.0.0.1:{}/postgres", port);

    // Wait for Postgres to accept connections
    let pool = {
        let mut last_err = None;
        let mut last_pool = None;

        for _ in 0..20 {
            match PgPoolOptions::new().max_connections(5).connect(&url).await {
                Ok(pool) => {
                    last_pool = Some(pool);
                    break;
                }
                Err(e) => {
                    last_err = Some(e);
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }

        last_pool.ok_or_else(|| {
            last_err.unwrap_or_else(|| sqlx::Error::Configuration("unknown error".into()))
        })?
    };

    // Apply Flyway-style migrations manually to avoid sqlx filename parsing expectations
    let mut entries: Vec<PathBuf> = fs::read_dir("./migrations/sql")?
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.extension().and_then(|s| s.to_str()) == Some("sql"))
        .collect();

    entries.sort();

    for path in entries {
        let sql = fs::read_to_string(&path)?;
        pool.execute(sql.as_str()).await?;
    }

    // Simple sanity check
    pool.execute("SELECT 1").await?;

    Ok(())
}
