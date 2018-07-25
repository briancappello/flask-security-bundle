from flask_unchained.bundles.sqlalchemy import ModelManager


class UserManager(ModelManager):
    model = 'User'
