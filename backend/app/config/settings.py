from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Deepfake Detection System"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    JWT_SECRET: str = "YOUR_SUPER_SECRET_KEY"
    DATABASE_URL: str = "mongodb://localhost:27017/deepfake_db"
    MODEL_PATH: str = "./models/deepfake_model.pt"
    UPLOAD_DIRECTORY: str = "./uploads"
    REPORT_DIRECTORY: str = "./reports"

    class Config:
        env_file = ".env"

settings = Settings()
