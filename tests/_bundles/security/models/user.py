from flask_security_bundle.models import User as BaseUser
from flask_sqlalchemy_bundle import db


class User(BaseUser):
    username = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
