from flask_controller_bundle import controller, prefix, resource, rule
from flask_security_bundle import SecurityController, UserResource

from .views import SiteController


routes = [
    controller('/', SecurityController),
    controller('/', SiteController),
    prefix('/api/v1', [
        # normally all these endpoint renames wouldn't be necessary, but we
        # need it here to not conflict with the HTML SecurityController routes
        controller('/auth', SecurityController, rules=[
            rule('/login', 'login', methods=['POST'],
                 endpoint='security_api.login'),
            rule('/check-auth-token', 'check_auth_token',
                 endpoint='security.check_auth_token'),
            rule('/logout', 'logout', methods=['GET', 'POST'],
                 endpoint='security_api.logout'),
            rule('/send-confirmation-email', 'send_confirmation_email',
                 methods=['POST'],
                 endpoint='security_api.send_confirmation_email'),
            rule('/confirm/<token>', 'confirm_email',
                 endpoint='security_api.confirm_email'),
            rule('/forgot-password', 'forgot_password', methods=['POST'],
                 endpoint='security_api.forgot_password'),
            rule('/reset-password/<token>', 'reset_password',
                 methods=['GET', 'POST'],
                 endpoint='security_api.reset_password'),
            rule('/change-password', 'change_password', methods=['POST'],
                 endpoint='security_api.change_password'),
        ]),
        resource('/users', UserResource),
    ]),
]
