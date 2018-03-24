from flask_security_bundle.config import BaseConfig as _BaseConfig
from flask_security_bundle.services import SQLAlchemyUserDatastore

from .models import User, Role


class BaseConfig(_BaseConfig):
    SECURITY_DATASTORE = SQLAlchemyUserDatastore(User, Role)
