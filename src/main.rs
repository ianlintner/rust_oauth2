#[actix_web::main]
async fn main() -> std::io::Result<()> {
    oauth2_server::run().await
}
