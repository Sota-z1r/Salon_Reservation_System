# app/config.py

import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # SQLite（ローカル開発用）
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "sqlite:///reservation.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LINE Messaging API
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LIFF_RESERVE_URL = os.getenv("LIFF_RESERVE_URL")
    LINE_ADMIN_TO = os.getenv("LINE_ADMIN_TO")
