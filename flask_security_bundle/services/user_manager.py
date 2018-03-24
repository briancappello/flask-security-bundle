from flask_sqlalchemy_bundle import ModelManager


class UserManager(ModelManager):
    model = 'User'
