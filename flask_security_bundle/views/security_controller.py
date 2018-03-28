from flask import current_app as app, request
from flask_controller_bundle import Controller, route
from flask_security import current_user
from flask_security.confirmable import confirm_email_token_status
from flask_security.views import _ctx as security_template_ctx
from flask_security.utils import get_message
from flask_unchained import injectable
from http import HTTPStatus
from werkzeug.datastructures import MultiDict

from ..decorators import anonymous_user_required, auth_required
from ..services import SecurityService


class SecurityController(Controller):
    def __init__(self, security_service: SecurityService = injectable):
        self.security_service = security_service

    @route(only_if=False)  # require check_auth_token to be explicitly enabled
    @auth_required()
    def check_auth_token(self):
        # the auth_required decorator verifies the token and sets current_user
        return self.jsonify({'user': current_user})

    @route(endpoint='security.login', methods=['GET', 'POST'])
    @anonymous_user_required(msg='You are already logged in',
                             category='success')
    def login(self):
        form = self._get_form('SECURITY_LOGIN_FORM')
        if form.validate_on_submit():
            self.security_service.login_user(form.user, form.remember.data)
            self.after_this_request(self._commit)
            if request.is_json:
                return self.jsonify({'token': form.user.get_auth_token(),
                                     'user': form.user})
            return self.redirect('SECURITY_POST_LOGIN_VIEW')

        elif form.errors:
            form = self.security_service.process_login_errors(form)
            if request.is_json:
                return self.jsonify({'error': form.errors.get('_error')[0]},
                                    code=HTTPStatus.UNAUTHORIZED)

        return self.render('login',
                           login_user_form=form,
                           **security_template_ctx('login'))

    @route(endpoint='security.logout')
    def logout(self):
        if current_user.is_authenticated:
            self.security_service.logout_user()

        if request.is_json:
            return '', HTTPStatus.NO_CONTENT
        return self.redirect('SECURITY_POST_LOGOUT_VIEW')

    @route(endpoint='security.register', methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_REGISTERABLE'))
    @anonymous_user_required
    def register(self):
        form_name = ('SECURITY_CONFIRM_REGISTER_FORM'
                     if app.config.get('SECURITY_CONFIRMABLE')
                     else 'SECURITY_REGISTER_FORM')
        form = self._get_form(form_name)

        if form.validate_on_submit():
            user = self.security_service.user_manager.create(**form.to_dict())
            self.security_service.register_user(user)

            return self.redirect('SECURITY_POST_REGISTER_VIEW')

        return self.render('register',
                           register_user_form=form,
                           **security_template_ctx('register'))

    @route(endpoint='security.send_confirmation', methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_CONFIRMABLE'))
    def send_confirmation_email(self):
        """
        View function which sends confirmation instructions
        """
        form = self._get_form('SECURITY_SEND_CONFIRMATION_FORM')
        if form.validate_on_submit():
            self.security_service.send_confirmation_instructions(form.user)
            self.flash(*get_message('CONFIRMATION_REQUEST',
                                    email=form.user.email))
            if request.is_json:
                return '', HTTPStatus.NO_CONTENT

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('send_confirmation_email',
                           send_confirmation_form=form,
                           **security_template_ctx('send_confirmation'))

    @route('/confirm/<token>', endpoint='security.confirm_email',
           only_if=lambda app: app.config.get('SECURITY_CONFIRMABLE'))
    def confirm_email(self, token):
        expired, invalid, user = confirm_email_token_status(token)

        if not user or invalid:
            invalid = True
            self.flash(*get_message('INVALID_CONFIRMATION_TOKEN'))

        already_confirmed = user is not None and user.confirmed_at is not None

        if expired and not already_confirmed:
            self.security_service.send_confirmation_instructions(user)
            self.flash(*get_message(
                'CONFIRMATION_EXPIRED', email=user.email,
                within=app.config.get('SECURITY_CONFIRM_EMAIL_WITHIN')))

        if invalid or (expired and not already_confirmed):
            return self.redirect('SECURITY_CONFIRM_ERROR_VIEW',
                                 'security.send_confirmation')

        if self.security_service.confirm_user(user):
            self.after_this_request(self._commit)
            msg = 'EMAIL_CONFIRMED'
        else:
            msg = 'ALREADY_CONFIRMED'
        self.flash(*get_message(msg))

        if user != current_user:
            self.security_service.logout_user()
            self.security_service.login_user(user)

        return self.redirect('SECURITY_POST_CONFIRM_VIEW',
                             'SECURITY_POST_LOGIN_VIEW')

    @route(endpoint='security.forgot_password', methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_RECOVERABLE'))
    @anonymous_user_required(msg='You are already logged in',
                             category='success')
    def forgot_password(self):
        form = self._get_form('SECURITY_FORGOT_PASSWORD_FORM')

        if form.validate_on_submit():
            self.security_service.send_reset_password_instructions(form.user)
            self.flash(*get_message('PASSWORD_RESET_REQUEST',
                                    email=form.user.email))
            if request.is_json:
                return '', HTTPStatus.NO_CONTENT

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('forgot_password',
                           forgot_password_form=form,
                           **security_template_ctx('forgot_password'))

    @route('/reset-password/<token>', methods=['GET', 'POST'],
           endpoint='security.reset_password',
           only_if=lambda app: app.config.get('SECURITY_RECOVERABLE'))
    @anonymous_user_required
    def reset_password(self, token):
        expired, invalid, user = \
            self.security_service.reset_password_token_status(token)

        if invalid:
            self.flash(*get_message('INVALID_RESET_PASSWORD_TOKEN'))
            return self.redirect('SECURITY_INVALID_RESET_TOKEN_REDIRECT')
        elif expired:
            self.security_service.send_reset_password_instructions(user)
            self.flash(*get_message(
                'PASSWORD_RESET_EXPIRED', email=user.email,
                within=app.config.get('SECURITY_RESET_PASSWORD_WITHIN')))
            return self.redirect('SECURITY_EXPIRED_RESET_TOKEN_REDIRECT')
        elif request.is_json and request.method == 'GET':
            return self.redirect(
                'SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT', token=token)

        form = self._get_form('SECURITY_RESET_PASSWORD_FORM')
        if form.validate_on_submit():
            self.security_service.reset_password(user, form.password.data)
            self.security_service.login_user(user)
            self.after_this_request(self._commit)
            self.flash(*get_message('PASSWORD_RESET'))
            if request.is_json:
                return self.jsonify({'token': user.get_auth_token(),
                                     'user': user})
            return self.redirect('SECURITY_POST_RESET_VIEW',
                                 'SECURITY_POST_LOGIN_VIEW')

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('reset_password',
                           reset_password_form=form,
                           reset_password_token=token,
                           **security_template_ctx('reset_password'))

    @route(endpoint='security.change_password', methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_CHANGEABLE'))
    @auth_required
    def change_password(self):
        form = self._get_form('SECURITY_CHANGE_PASSWORD_FORM')

        if form.validate_on_submit():
            self.security_service.change_password(current_user,
                                                  form.new_password.data)
            self.after_this_request(self._commit)
            self.flash(*get_message('PASSWORD_CHANGE'))
            if request.is_json:
                return self.jsonify({'token': current_user.get_auth_token()})
            return self.redirect('SECURITY_POST_CHANGE_VIEW',
                                 'SECURITY_POST_LOGIN_VIEW')

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('change_password',
                           change_password_form=form,
                           **security_template_ctx('change_password'))

    def _get_form(self, name):
        form_cls = app.config.get(name)
        if request.is_json:
            return form_cls(MultiDict(request.get_json()))
        return form_cls(request.form)

    def _commit(self, response=None):
        self.security_service.security.datastore.commit()
        return response
