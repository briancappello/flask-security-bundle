from flask_unchained import AppConfig


class BaseConfig(AppConfig):
    SECRET_KEY = 'not-secret-key'
    SECURITY_PASSWORD_SALT = 'not-secret-salt'


class TestConfig(BaseConfig):
    TESTING = True

    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
