from flask_sqlalchemy_bundle import db

from flask_security_bundle.models import Role as BaseRole


class Role(BaseRole):
    description = db.Column(db.Text, nullable=True)
