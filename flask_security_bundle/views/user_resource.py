from flask_api_bundle import ModelResource
from flask_controller_bundle.constants import CREATE, GET, PATCH
from flask_unchained import injectable

from ..decorators import anonymous_user_required, auth_required_same_user
from ..services import SecurityService


class UserResource(ModelResource):
    model = 'User'

    include_methods = {CREATE, GET, PATCH}
    method_decorators = {
        CREATE: [anonymous_user_required],
        GET: [auth_required_same_user],
        PATCH: [auth_required_same_user],
    }

    def __init__(self, security_service: SecurityService = injectable):
        super().__init__()
        self.security_service = security_service

    def create(self, user, errors):
        if errors:
            return self.errors(errors)

        user_logged_in = self.security_service.register_user(user)
        if user_logged_in:
            return self.created({'token': user.get_auth_token(),
                                 'user': user}, commit=False)
        return self.created({'user': user}, commit=False)
