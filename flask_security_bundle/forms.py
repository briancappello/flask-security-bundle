from flask import current_app as app, request
from flask_security import current_user
from flask_security.forms import (
    EqualTo,
    ForgotPasswordForm,
    Length,
    NextFormMixin,
    PasswordlessLoginForm,
    RegisterFormMixin,
    Required,
    SendConfirmationForm,
    SubmitField,
    UniqueEmailFormMixin,
    get_form_field_label,
    email_required,
    email_validator,
)
from flask_security.utils import get_message
from flask_sqlalchemy_bundle import ModelForm
from flask_unchained import unchained, injectable
from wtforms import fields

from .services import SecurityService
from .utils import verify_and_update_password


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        if app.testing:
            self.TIME_LIMIT = None
        super().__init__(*args, **kwargs)


password_length = Length(min=8, max=255,
                         message='Password must be at least 8 characters long.')
password_required = Required(message='Password is required')


@unchained.inject('security_service')
class LoginForm(BaseForm, NextFormMixin):
    """The default login form"""
    class Meta:
        model = 'User'

    email = fields.StringField(get_form_field_label('email'),
                               validators=[email_required, email_validator])
    password = fields.PasswordField(get_form_field_label('password'))
    remember = fields.BooleanField(get_form_field_label('remember_me'))
    submit = fields.SubmitField(get_form_field_label('login'))

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
            self.email.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not self.user.password:
            self.password.errors.append(get_message('PASSWORD_NOT_SET')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if (not self.security_service.security.login_without_confirmation
                and self.security_service.security.confirmable
                and self.user.confirmed_at is None):
            self.email.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True


class PasswordFormMixin:
    password = fields.PasswordField(get_form_field_label('password'))


class PasswordConfirmFormMixin:
    password_confirm = fields.PasswordField(
        get_form_field_label('retype_password'),
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')])


class ChangePasswordForm(BaseForm, PasswordFormMixin):
    class Meta:
        model = 'User'
        model_fields = {'new_password': 'password'}

    new_password = fields.PasswordField(get_form_field_label('new_password'))
    new_password_confirm = fields.PasswordField(
        get_form_field_label('retype_password'),
        validators=[EqualTo('new_password', message='RETYPE_PASSWORD_MISMATCH'),
                    password_required]
    )

    submit = fields.SubmitField(get_form_field_label('change_password'))

    def validate(self):
        result = super().validate()

        if not verify_and_update_password(self.password.data, current_user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if self.password.data == self.new_password.data:
            self.new_password.errors.append(
                get_message('PASSWORD_IS_THE_SAME')[0])
            return False
        return result


class BaseConfirmRegisterForm(BaseForm, RegisterFormMixin, UniqueEmailFormMixin):
    class Meta:
        model = 'User'


class ConfirmRegisterForm(BaseConfirmRegisterForm, PasswordFormMixin):
    pass


class RegisterForm(ConfirmRegisterForm, PasswordConfirmFormMixin, NextFormMixin):
    class Meta:
        model = 'User'


class ResetPasswordForm(BaseForm, PasswordFormMixin, PasswordConfirmFormMixin):
    class Meta:
        model = 'User'
        model_fields = {'password_confirm': 'password'}

    submit = SubmitField(get_form_field_label('reset_password'))
