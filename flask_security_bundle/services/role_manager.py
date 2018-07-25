from flask_unchained.bundles.sqlalchemy import ModelManager


class RoleManager(ModelManager):
    model = 'Role'
