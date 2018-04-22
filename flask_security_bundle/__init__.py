"""
    flask_security_bundle
    ~~~~~~~~~~~~~~~~~~~~~

    Authentication and authorization support for Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.1.1'


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
