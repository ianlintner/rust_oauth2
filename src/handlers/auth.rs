// Compatibility facade.
//
// Social login (models/service/handlers) was extracted to `oauth2-social-login`.
// Keep `rust_oauth2_server::handlers::auth::*` stable for downstream users.
pub use oauth2_social_login::handlers::auth::*;
