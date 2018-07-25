import inspect

from flask import current_app as app, request
from flask_security import current_user
from flask_security.forms import (
    EqualTo,
    Field,
    NextFormMixin,
    StringField,
    SubmitField,
    _datastore,
)
from flask_unchained.bundles.sqlalchemy import ModelForm
from flask_unchained import unchained, injectable, lazy_gettext as _
from wtforms import ValidationError, fields

from .services import SecurityService
from .utils import verify_and_update_password


password_equal = EqualTo(
    'password', message=_('flask_security_bundle.error.retype_password_mismatch'))
new_password_equal = EqualTo(
    'new_password', message=_('flask_security_bundle.error.retype_password_mismatch'))


def unique_user_email(form, field):
    if _datastore.get_user(field.data) is not None:
        msg = _('flask_security_bundle.error.email_already_associated', email=field.data)
        raise ValidationError(msg)


def valid_user_email(form, field):
    form.user = _datastore.get_user(field.data)
    if form.user is None:
        raise ValidationError(_('flask_security_bundle.error.user_does_not_exist'))


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        if app.testing:
            self.TIME_LIMIT = None
        super().__init__(*args, **kwargs)


@unchained.inject('security_service')
class LoginForm(BaseForm, NextFormMixin):
    """The default login form"""
    class Meta:
        model = 'User'

    email = fields.StringField(_('flask_security_bundle.form_field.email'))
    password = fields.PasswordField(_('flask_security_bundle.form_field.password'))
    remember = fields.BooleanField(_('flask_security_bundle.form_field.remember_me'))
    submit = fields.SubmitField(_('flask_security_bundle.form_submit.login'))

    def __init__(self, *args, security_service: SecurityService = injectable,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.security_service = security_service
        self.user = None

        if not self.next.data:
            self.next.data = request.args.get('next', '')
        self.remember.default = app.config.get('SECURITY_DEFAULT_REMEMBER_ME')

    def get_user(self):
        return self.security_service.user_manager.get_by(email=self.email.data)

    def validate(self):
        if not super().validate():
            return False

        self.user = self.get_user()

        if self.user is None:
            self.email.errors.append(
                _('flask_security_bundle.error.user_does_not_exist'))
            return False
        if not self.user.password:
            self.password.errors.append(
                _('flask_security_bundle.error.password_not_set'))
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(
                _('flask_security_bundle.error.invalid_password'))
            return False
        if (not self.security_service.security.login_without_confirmation
                and self.security_service.security.confirmable
                and self.user.confirmed_at is None):
            self.email.errors.append(
                _('flask_security_bundle.error.confirmation_required'))
            return False
        if not self.user.is_active:
            self.email.errors.append(
                _('flask_security_bundle.error.disabled_account'))
            return False
        return True


class ForgotPasswordForm(BaseForm):
    class Meta:
        model = 'User'

    user = None
    email = StringField(_('flask_security_bundle.form_field.email'),
                        validators=[valid_user_email])
    submit = fields.SubmitField(_('flask_security_bundle.form_submit.recover_password'))


class PasswordFormMixin:
    password = fields.PasswordField(_('flask_security_bundle.form_field.password'))


class PasswordConfirmFormMixin:
    password_confirm = fields.PasswordField(
        _('flask_security_bundle.form_field.retype_password'),
        validators=[password_equal])


class ChangePasswordForm(BaseForm, PasswordFormMixin):
    class Meta:
        model = 'User'
        model_fields = {'new_password': 'password',
                        'new_password_confirm': 'password'}

    new_password = fields.PasswordField(
        _('flask_security_bundle.form_field.new_password'))
    new_password_confirm = fields.PasswordField(
        _('flask_security_bundle.form_field.retype_password'),
        validators=[new_password_equal])

    submit = fields.SubmitField(_('flask_security_bundle.form_submit.change_password'))

    def validate(self):
        result = super().validate()

        if not verify_and_update_password(self.password.data, current_user):
            self.password.errors.append(
                _('flask_security_bundle.error.invalid_password'))
            return False
        if self.password.data == self.new_password.data:
            self.new_password.errors.append(
                _('flask_security_bundle.error.password_is_the_same'))
            return False
        return result


class ConfirmRegisterForm(BaseForm, PasswordFormMixin):
    class Meta:
        model = 'User'

    email = StringField(_('flask_security_bundle.form_field.email'),
                        validators=[unique_user_email])

    submit = SubmitField(_('flask_security_bundle.form_submit.register'))

    def to_dict(self):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                hasattr(_datastore.user_model, member.name)

        fields = inspect.getmembers(self, is_field_and_user_attr)
        return dict((key, value.data) for key, value in fields)


class RegisterForm(ConfirmRegisterForm, PasswordConfirmFormMixin, NextFormMixin):
    class Meta:
        model = 'User'


class ResetPasswordForm(BaseForm, PasswordFormMixin, PasswordConfirmFormMixin):
    class Meta:
        model = 'User'
        model_fields = {'password_confirm': 'password'}

    submit = SubmitField(_('flask_security_bundle.form_submit.reset_password'))


class SendConfirmationForm(BaseForm):
    class Meta:
        model = 'User'

    user = None
    email = StringField(_('flask_security_bundle.form_field.email'),
                        validators=[valid_user_email])
    submit = SubmitField(_('flask_security_bundle.form_submit.send_confirmation'))

    def __init__(self, *args, **kwargs):
        super(SendConfirmationForm, self).__init__(*args, **kwargs)
        if request.method == 'GET':
            self.email.data = request.args.get('email', None)

    def validate(self):
        if not super(SendConfirmationForm, self).validate():
            return False
        if self.user.confirmed_at is not None:
            self.email.errors.append(
                _('flask_security_bundle.error.already_confirmed'))
            return False
        return True
