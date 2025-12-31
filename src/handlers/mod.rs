// Compatibility facade.
//
// Most HTTP handlers were extracted to `oauth2-actix`.
// Social-login handlers live in `oauth2-social-login` but remain available here via a facade.

pub mod admin {
	pub use oauth2_actix::handlers::admin::*;
}

pub mod client {
	pub use oauth2_actix::handlers::client::*;
}

pub mod events {
	pub use oauth2_actix::handlers::events::*;
}

pub mod oauth {
	pub use oauth2_actix::handlers::oauth::*;
}

pub mod token {
	pub use oauth2_actix::handlers::token::*;
}

pub mod wellknown {
	pub use oauth2_actix::handlers::wellknown::*;
}

pub mod auth;
