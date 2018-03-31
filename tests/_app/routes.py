from flask_controller_bundle import controller, get, post, prefix, resource
from flask_security_bundle import SecurityController, UserResource

from .views import SiteController


routes = [
    controller('/', SecurityController),
    controller('/', SiteController),

    # normally all these api endpoint renames wouldn't be necessary, but we
    # need it here to not conflict with the HTML SecurityController routes
    controller('/auth', SecurityController, rules=[
        get('/reset-password/<token>', SecurityController.reset_password,
            endpoint='security_api.reset_password'),
    ]),
    prefix('/api/v1', [
        controller('/auth', SecurityController, rules=[
            get('/check-auth-token', SecurityController.check_auth_token,
                only_if=True, endpoint='security.check_auth_token'),
            post('/login', SecurityController.login,
                 endpoint='security_api.login'),
            get('/logout', SecurityController.logout,
                endpoint='security_api.logout'),
            post('/send-confirmation-email',
                 SecurityController.send_confirmation_email,
                 endpoint='security_api.send_confirmation_email'),
            post('/forgot-password', SecurityController.forgot_password,
                 endpoint='security_api.forgot_password'),
            post('/reset-password/<token>', SecurityController.reset_password,
                 endpoint='security_api.post_reset_password'),
            post('/change-password', SecurityController.change_password,
                 endpoint='security_api.change_password'),
        ]),
        resource('/users', UserResource),
    ]),
]
