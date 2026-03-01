import os
from dotenv import load_dotenv

load_dotenv()


def _safe_key(key):
    if not key or len(key) < 32:
        return "dev-secret-key-change-me-please-32chars"
    return key


class Config:
    SECRET_KEY = _safe_key(os.getenv("SECRET_KEY"))
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = _safe_key(os.getenv("JWT_SECRET_KEY", SECRET_KEY))
