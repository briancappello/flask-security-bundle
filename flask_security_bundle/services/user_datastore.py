from flask_security import SQLAlchemyUserDatastore as BaseUserDatastore
from flask_unchained import injectable, unchained


@unchained.inject('db')
class SQLAlchemyUserDatastore(BaseUserDatastore):
    def __init__(self, user_model, role_model, db=injectable):
        super().__init__(db, user_model, role_model)

    def create_user(self, hash_password=False, **kwargs):
        """
        Overridden to make sure the User model doesn't double-hash passwords
        """
        super().create_user(**kwargs, hash_password=hash_password)

    def _prepare_create_user_args(self, **kwargs):
        """
        Overridden to not set default kwargs.

        The User class defines its own defaults.
        """
        # load roles by name if necessary
        roles = kwargs.get('roles', [])
        for i, role in enumerate(roles):
            if not isinstance(role, self.role_model):
                roles[i] = self.find_role(role)
        kwargs['roles'] = roles
        return kwargs
