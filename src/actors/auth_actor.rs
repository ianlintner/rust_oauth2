// Compatibility facade.
//
// The actor implementations were extracted to `oauth2-actix`. This file exists
// only to preserve the legacy module path `rust_oauth2_server::actors::auth_actor::*`.
pub use oauth2_actix::actors::auth_actor::*;
