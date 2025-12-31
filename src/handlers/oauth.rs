// Compatibility facade.
//
// The HTTP handlers were extracted to `oauth2-actix`. This file exists only to
// preserve the legacy module path `rust_oauth2_server::handlers::oauth::*`.
pub use oauth2_actix::handlers::oauth::*;
