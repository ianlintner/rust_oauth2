use oauth2_config::{ProviderConfig, SocialConfig};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Deserialize)]
pub struct SocialLoginConfig {
    pub google: Option<ProviderConfig>,
    pub microsoft: Option<ProviderConfig>,
    pub github: Option<ProviderConfig>,
    pub azure: Option<ProviderConfig>,
    pub okta: Option<ProviderConfig>,
    pub auth0: Option<ProviderConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SocialUserInfo {
    pub provider: String,
    pub provider_user_id: String,
    pub email: String,
    pub name: Option<String>,
    pub picture: Option<String>,
}

impl SocialLoginConfig {
    pub fn from_env() -> Self {
        Self {
            google: Self::provider_from_env("GOOGLE"),
            microsoft: Self::provider_from_env("MICROSOFT"),
            github: Self::provider_from_env("GITHUB"),
            azure: Self::provider_from_env("AZURE"),
            okta: Self::provider_from_env("OKTA"),
            auth0: Self::provider_from_env("AUTH0"),
        }
    }

    /// Create SocialLoginConfig from the main config's social section.
    pub fn from_config_social(social: &SocialConfig) -> Self {
        Self {
            google: social.google.clone(),
            microsoft: social.microsoft.clone(),
            github: social.github.clone(),
            azure: social.azure.clone(),
            okta: social.okta.clone(),
            auth0: social.auth0.clone(),
        }
    }

    fn provider_from_env(prefix: &str) -> Option<ProviderConfig> {
        let client_id = std::env::var(format!("OAUTH2_{}_CLIENT_ID", prefix)).ok();
        let client_secret = std::env::var(format!("OAUTH2_{}_CLIENT_SECRET", prefix)).ok();

        // Only create config if both client_id and client_secret are set
        if client_id.is_some() && client_secret.is_some() {
            let redirect_uri = std::env::var(format!("OAUTH2_{}_REDIRECT_URI", prefix))
                .ok()
                .or_else(|| {
                    Some(format!(
                        "http://localhost:8080/auth/callback/{}",
                        prefix.to_lowercase()
                    ))
                });

            Some(ProviderConfig {
                enabled: true,
                client_id,
                client_secret,
                redirect_uri,
                tenant_id: std::env::var(format!("OAUTH2_{}_TENANT_ID", prefix)).ok(),
                domain: std::env::var(format!("OAUTH2_{}_DOMAIN", prefix)).ok(),
            })
        } else {
            None
        }
    }
}
