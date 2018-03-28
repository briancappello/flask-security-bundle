from flask_unchained import Bundle

from .decorators import (
    anonymous_user_required,
    auth_required,
    auth_required_same_user,
)
from .services import SecurityService, UserManager, RoleManager
from .views import SecurityController, UserResource


class FlaskSecurityBundle(Bundle):
    blueprint_names = []
    command_group_names = []
