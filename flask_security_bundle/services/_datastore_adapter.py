from flask_security.datastore import UserDatastore as BaseDatastore
from flask_security.utils import get_identity_attributes
from flask_sqlalchemy_bundle import SessionManager

from .role_manager import RoleManager
from .user_manager import UserManager


class DatastoreAdapter(BaseDatastore):
    """
    A version of flask_security's UserDatastore that works with
    flask_unchained's dependency-injected services
    """
    def __init__(self,
                 user_manager: UserManager,
                 role_manager: RoleManager,
                 session_manager: SessionManager = None):
        super().__init__(user_manager.model, role_manager.model)
        self.user_manager = user_manager
        self.role_manager = role_manager
        self.session_manager = session_manager

    def put(self, instance):
        self.session_manager.save(instance)

    def delete(self, instance):
        self.session_manager.delete(instance)

    def commit(self):
        if self.session_manager:
            self.session_manager.commit()

    # FIXME-identity
    def get_user(self, identity):
        if self._is_numeric(identity):
            return self.user_manager.get(identity)
        for attr in get_identity_attributes():
            user = self.user_manager.get_by(**{attr: identity})
            if user:
                return user

    def find_user(self, **kwargs):
        return self.user_manager.get_by(**kwargs)

    def find_role(self, **kwargs):
        return self.role_manager.get_by(**kwargs)

    def _is_numeric(self, value):
        try:
            return bool(int(value)) or True
        except (TypeError, ValueError):
            return False

    def _prepare_create_user_args(self, **kwargs):
        roles = kwargs.get('roles', [])
        for i, role in enumerate(roles):
            if isinstance(role, str):
                roles[i] = self.role_manager.get_by(name=role)
        kwargs['roles'] = roles
        return kwargs

    def _prepare_role_modify_args(self, user, role):
        if isinstance(user, str):
            user = self.user_manager.get_by(email=user)
        if isinstance(role, str):
            role = self.role_manager.get_by(name=role)
        return user, role
