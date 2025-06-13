from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # database configuration
    database_port: str
    database_name: str
    database_hostname: str
    database_password: str
    database_username: str
    async_database_url: str
    
    # JWT and security
    secret_key: str
    algorithm: str 
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    forget_password_secret_key: str
    password_reset_token_expire_minutes: int
    
    # cloudinary configuration
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    folder_name: str
    
    # Email configuration
    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_from_name: str
    mail_from: str
    
    sync_database_url: str

    # Load variables form .env file
    class Config:
        env_file = ".env"

# create setting instance
settings = Settings()