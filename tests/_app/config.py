from flask_unchained import AppConfig


class BaseConfig(AppConfig):
    SECRET_KEY = 'not-secret-key'


class TestConfig(BaseConfig):
    TESTING = True
