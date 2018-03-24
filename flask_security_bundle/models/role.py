from flask_security import RoleMixin
from flask_sqlalchemy_bundle import db

from .user_role import UserRole


class Role(db.Model, RoleMixin):
    class Meta:
        lazy_mapped = True

    name = db.Column(db.String(64), unique=True, index=True)

    role_users = db.relationship('UserRole', back_populates='role',
                                 cascade='all, delete-orphan')
    users = db.association_proxy('role_users', 'user',
                                 creator=lambda user: UserRole(user=user))

    __repr_props__ = ('id', 'name')
