from flask import current_app as app, request
from flask_unchained import Controller, route, lazy_gettext as _
from flask_unchained import injectable
from flask_unchained.bundles.sqlalchemy import SessionManager
from http import HTTPStatus
from werkzeug.datastructures import MultiDict

from ..decorators import anonymous_user_required, auth_required
from ..extensions import Security
from ..services import SecurityService
from ..utils import current_user, confirm_email_token_status, reset_password_token_status


class SecurityController(Controller):
    def __init__(self,
                 security: Security = injectable,
                 security_service: SecurityService = injectable,
                 session_manager: SessionManager = injectable):
        self.security = security
        self.security_service = security_service
        self.session_manager = session_manager

    # require check_auth_token to be explicitly enabled
    @route(only_if=False)
    @auth_required()
    def check_auth_token(self):
        # the auth_required decorator verifies the token and sets current_user,
        # just need to return a success response
        return self.jsonify({'user': current_user})

    @route(methods=['GET', 'POST'])
    @anonymous_user_required(msg='You are already logged in', category='success')
    def login(self):
        form = self._get_form('SECURITY_LOGIN_FORM')
        if (form.validate_on_submit()
                and self.security_service.login_user(form.user, form.remember.data)):
            self.after_this_request(self._commit)
            if request.is_json:
                return self.jsonify({'token': form.user.get_auth_token(),
                                     'user': form.user})
            self.flash(_('flask_security_bundle.flash.login', user=form.user.first_name),
                       category='success')
            return self.redirect('SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')

        elif form.errors:
            form = self.security_service.process_login_errors(form)
            if request.is_json:
                return self.jsonify({'error': form.errors.get('_error')[0]},
                                    code=HTTPStatus.UNAUTHORIZED)

        return self.render('login',
                           login_user_form=form,
                           **self.security.run_ctx_processor('login'))

    @route()
    def logout(self):
        if current_user.is_authenticated:
            self.security_service.logout_user()

        if request.is_json:
            return '', HTTPStatus.NO_CONTENT

        self.flash(_('flask_security_bundle.flash.logout'), category='success')
        return self.redirect('SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT')

    @route(methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_REGISTERABLE'))
    @anonymous_user_required
    def register(self):
        form = self._get_form('SECURITY_REGISTER_FORM')
        if form.validate_on_submit():
            user = self.security_service.user_manager.create(**form.to_dict())
            self.security_service.register_user(user)
            return self.redirect('SECURITY_POST_REGISTER_REDIRECT_ENDPOINT')

        return self.render('register',
                           register_user_form=form,
                           **self.security.run_ctx_processor('register'))

    @route(methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_CONFIRMABLE'))
    def send_confirmation_email(self):
        """
        View function which sends confirmation instructions
        """
        form = self._get_form('SECURITY_SEND_CONFIRMATION_FORM')
        if form.validate_on_submit():
            self.security_service.send_email_confirmation_instructions(form.user)
            self.flash(_('flask_security_bundle.flash.confirmation_request',
                         email=form.user.email), category='info')
            if request.is_json:
                return '', HTTPStatus.NO_CONTENT

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('send_confirmation_email',
                           send_confirmation_form=form,
                           **self.security.run_ctx_processor('send_confirmation'))

    @route('/confirm/<token>',
           only_if=lambda app: app.config.get('SECURITY_CONFIRMABLE'))
    def confirm_email(self, token):
        expired, invalid, user = confirm_email_token_status(token)
        if not user or invalid:
            invalid = True
            self.flash(_('flask_security_bundle.flash.invalid_confirmation_token'),
                       category='error')

        already_confirmed = user is not None and user.confirmed_at is not None
        if expired and not already_confirmed:
            self.security_service.send_email_confirmation_instructions(user)
            self.flash(_('flask_security_bundle.flash.confirmation_expired',
                         email=user.email,
                         within=app.config.get('SECURITY_CONFIRM_EMAIL_WITHIN')),
                       category='error')

        if invalid or (expired and not already_confirmed):
            return self.redirect('SECURITY_CONFIRM_ERROR_REDIRECT_ENDPOINT',
                                 'security_controller.send_confirmation_email')

        if self.security_service.confirm_user(user):
            self.after_this_request(self._commit)
            self.flash(_('flask_security_bundle.flash.email_confirmed'),
                       category='success')
        else:
            self.flash(_('flask_security_bundle.flash.already_confirmed'),
                       category='info')

        if user != current_user:
            self.security_service.logout_user()
            self.security_service.login_user(user)

        return self.redirect('SECURITY_POST_CONFIRM_REDIRECT_ENDPOINT',
                             'SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')

    @route(methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_RECOVERABLE'))
    @anonymous_user_required(msg='You are already logged in',
                             category='success')
    def forgot_password(self):
        form = self._get_form('SECURITY_FORGOT_PASSWORD_FORM')
        if form.validate_on_submit():
            self.security_service.send_reset_password_instructions(form.user)
            self.flash(_('flask_security_bundle.flash.password_reset_request',
                         email=form.user.email), category='info')
            if request.is_json:
                return '', HTTPStatus.NO_CONTENT

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('forgot_password',
                           forgot_password_form=form,
                           **self.security.run_ctx_processor('forgot_password'))

    @route('/reset-password/<string:token>', methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_RECOVERABLE'))
    @anonymous_user_required
    def reset_password(self, token):
        expired, invalid, user = reset_password_token_status(token)
        if invalid:
            self.flash(_('flask_security_bundle.flash.invalid_reset_password_token'),
                       category='error')
            return self.redirect('SECURITY_INVALID_RESET_TOKEN_REDIRECT')
        elif expired:
            self.security_service.send_reset_password_instructions(user)
            self.flash(_('flask_security_bundle.flash.password_reset_expired',
                         email=user.email,
                         within=app.config.get('SECURITY_RESET_PASSWORD_WITHIN')),
                       category='error')
            return self.redirect('SECURITY_EXPIRED_RESET_TOKEN_REDIRECT')

        spa_redirect = app.config.get('SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT')
        if request.method == 'GET' and spa_redirect:
            return self.redirect(spa_redirect, token=token, _external=True)

        form = self._get_form('SECURITY_RESET_PASSWORD_FORM')
        if form.validate_on_submit():
            self.security_service.reset_password(user, form.password.data)
            self.security_service.login_user(user)
            self.after_this_request(self._commit)
            self.flash(_('flask_security_bundle.flash.password_reset'),
                       category='success')
            if request.is_json:
                return self.jsonify({'token': user.get_auth_token(),
                                     'user': user})
            return self.redirect('SECURITY_POST_RESET_REDIRECT_ENDPOINT',
                                 'SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('reset_password',
                           reset_password_form=form,
                           reset_password_token=token,
                           **self.security.run_ctx_processor('reset_password'))

    @route(methods=['GET', 'POST'],
           only_if=lambda app: app.config.get('SECURITY_CHANGEABLE'))
    @auth_required
    def change_password(self):
        form = self._get_form('SECURITY_CHANGE_PASSWORD_FORM')
        if form.validate_on_submit():
            self.security_service.change_password(
                current_user._get_current_object(),
                form.new_password.data)
            self.after_this_request(self._commit)
            self.flash(_('flask_security_bundle.flash.password_change'),
                       category='success')
            if request.is_json:
                return self.jsonify({'token': current_user.get_auth_token()})
            return self.redirect('SECURITY_POST_CHANGE_REDIRECT_ENDPOINT',
                                 'SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')

        elif form.errors and request.is_json:
            return self.errors(form.errors)

        return self.render('change_password',
                           change_password_form=form,
                           **self.security.run_ctx_processor('change_password'))

    def _get_form(self, name):
        form_cls = app.config.get(name)
        if request.is_json:
            return form_cls(MultiDict(request.get_json()))
        return form_cls(request.form)

    def _commit(self, response=None):
        self.session_manager.commit()
        return response
