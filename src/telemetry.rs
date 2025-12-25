use opentelemetry::{global, KeyValue};
use opentelemetry_sdk::{
    trace::{self, RandomIdGenerator, Sampler},
    Resource,
};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

pub fn init_telemetry(service_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    // For now, use a simplified tracing setup without OTLP
    // In production, configure OTLP exporter with proper endpoint
    
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));

    // JSON formatting for structured logging
    let formatting_layer = tracing_subscriber::fmt::layer()
        .json()
        .with_current_span(true)
        .with_span_list(true);

    tracing_subscriber::registry()
        .with(env_filter)
        .with(formatting_layer)
        .init();

    Ok(())
}

pub fn shutdown_telemetry() {
    global::shutdown_tracer_provider();
}
