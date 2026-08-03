import os
from datetime import timedelta

# Utilise API_KEY en majuscules pour correspondre à tes autres imports
API_KEY = os.environ.get("GEMINI_API_KEY")

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest"
]

class Config:
    # --- Base de données ---
    # Render fournit DATABASE_URL au format "postgres://".
    # SQLAlchemy exige le préfixe "postgresql://" depuis SQLAlchemy 1.4+.
    _raw_db_url = os.environ.get("DATABASE_URL", "")
    SQLALCHEMY_DATABASE_URI = _raw_db_url.replace("postgres://", "postgresql://", 1) \
        if _raw_db_url.startswith("postgres://") else _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-moi-en-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # --- Token de vérification d'email / reset password (signature, pas JWT) ---
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "change-moi-aussi")
    EMAIL_TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24  # 24h pour cliquer le lien de vérification

   # --- Envoi d'email (Flask-Mail), compatible avec n'importe quel SMTP ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp-relay.brevo.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    
    # Lecture dynamique de TLS / SSL depuis Render (avec valeurs par défaut sécurisées pour SSL/465)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() in ["true", "1"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "true").lower() in ["true", "1"]
    
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "tmyquizmaker@gmail.com")
    # URL de base de votre app pour construire les liens de vérification/reset
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")
