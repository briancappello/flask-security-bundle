"""
    flask_security_bundle
    ~~~~~~~~~~~~~~~~~~~~~

    Authentication and authorization support for Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.3.0'


from flask_security import current_user  # alias this here
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
    command_group_names = ['users', 'roles']

    @classmethod
    def after_init_app(cls, app):
        from flask_wtf.csrf import generate_csrf

        # send CSRF token in the cookie
        @app.after_request
        def set_csrf_cookie(response):
            if response:
                response.set_cookie('csrf_token', generate_csrf())
            return response
