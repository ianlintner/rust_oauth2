pub use oauth2_storage_factory::{create_storage, DynStorage, ObservedStorage, Storage};

// Compatibility module path.
//
// Historically `ObservedStorage` lived under `rust_oauth2_server::storage::observed::*`.
pub mod observed;

/// Backward-compatible module path for the SQLx adapter.
pub use oauth2_storage_factory::sqlx;

/// Backward-compatible module path for the Mongo adapter.
#[cfg(feature = "mongo")]
pub use oauth2_storage_factory::mongo;

