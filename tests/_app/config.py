from flask_unchained import AppConfig


class Config(AppConfig):
    SECRET_KEY = 'not-secret-key'
