import os

class Settings:
    """
    Konfigurasi aplikasi
    """
    # JWT Settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-this-in-production-min-32-chars-hotel-reservation-2025"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Settings
    APP_NAME: str = "Hotel Reservation System"
    APP_VERSION: str = "1.0.0"

# Buat instance settings
settings = Settings()