from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str

    access_token_secret_key: str
    refresh_token_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    folder_name: str

    forget_password_secret_key: str
    password_reset_token_expire_minutes: int

    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_from: str
    mail_from_name: str

    allowed_domains: list[str]
    sync_database_url: str
    async_database_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  # extra="ignore" will skip unknown fields

settings = Settings()
