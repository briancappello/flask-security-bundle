from flask_unchained import current_app

from .user_manager import UserManager


class DatastoreAdapter:
    """
    A version of flask_security's UserDatastore that works with
    flask_unchained's dependency-injected services
    """
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    # FIXME-identity
    def get_user(self, identity):
        if self._is_numeric(identity):
            return self.user_manager.get(identity)
        for attr in get_identity_attributes():
            user = self.user_manager.get_by(**{attr: identity})
            if user:
                return user

    # FIXME: the :meth:`_check_token` in `decorators/auth_required` depends on this
    def find_user(self, **kwargs):
        return self.user_manager.get_by(**kwargs)

    def _is_numeric(self, value):
        try:
            return bool(int(value)) or True
        except (TypeError, ValueError):
            return False


# FIXME-identity
def get_identity_attributes():
    attrs = current_app.config['SECURITY_USER_IDENTITY_ATTRIBUTES']
    try:
        attrs = [f.strip() for f in attrs.split(',')]
    except AttributeError:
        pass
    return attrs
