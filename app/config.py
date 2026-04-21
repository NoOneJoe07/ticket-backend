import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

class Config:
    """Configuration de base (commune à Dev et Prod)."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///ticket_booking.db"  # fallback si .env absent
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS (si tu veux restreindre plus tard)
    CORS_HEADERS = "Content-Type"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
